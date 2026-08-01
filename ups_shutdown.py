"""
UPS-triggered orderly shutdown for the k3s cluster and supporting infrastructure.

Sequence on critical battery:
  1. kubectl drain worker nodes   — SSH intel_sbc → orangepi5b → ubuntu master
  2. kubectl drain master nodes   — same path (all but last master)
  3. SSH shutdown workers         — direct password SSH from intel_sbc
  4. Proxmox API shutdown masters — ACPI shutdown via pve API (no SSH to VMs needed)
  5. SSH shutdown Proxmox hosts   — direct password SSH from intel_sbc
  6. intel_sbc + NAS:
       a. Schedule intel_sbc host OS shutdown (+5 min delay via SSH)
       b. Proxmox API ACPI shutdown HAOS VM — AppDaemon killed when VM stops (~90s)
       c. Synology NAS API shutdown — NAS takes 2-3 min; intel_sbc still accessible throughout

Power-restored abort cancels the armed timer at any point before execution starts.

Test mode — fire the HA event 'ups_shutdown_test' from Developer Tools to run a
full connectivity check without executing any destructive commands.

Configuration lives in apps.yaml.
python_packages required in AppDaemon addon config: paramiko, requests
"""

import os
import threading
import time

import paramiko
import requests
import urllib3
import appdaemon.plugins.hass.hassapi as hass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class UPSShutdown(hass.Hass):

    def initialize(self):
        self._timer       = None
        self._in_progress = False
        self._lock        = threading.Lock()

        self.battery_low   = int(self.args.get("battery_low",    20))
        self.runtime_low   = int(self.args.get("runtime_low",     5))
        self.pre_delay     = int(self.args.get("pre_delay",     120))
        self.ssh_timeout   = int(self.args.get("ssh_timeout",    30))
        self.drain_timeout = int(self.args.get("drain_timeout", 120))

        self.listen_state(self._on_status,  "sensor.myups_status_data")
        self.listen_state(self._on_battery, "sensor.myups_battery_charge")
        self.listen_state(self._on_runtime, "sensor.ups_estimated_runtime")
        self.listen_event(self._on_test_event, "ups_shutdown_test")

        self.log(
            "UPS Shutdown ready — battery_low=%d%% runtime_low=%dmin pre_delay=%ds  "
            "(fire event 'ups_shutdown_test' to run connectivity test)",
            self.battery_low, self.runtime_low, self.pre_delay,
        )

    # ── sensor listeners ────────────────────────────────────────────────────

    def _on_status(self, entity, attribute, old, new, kwargs):
        if new and "OB" in new:
            self.log("UPS on battery (status=%s) — evaluating shutdown", new)
            self._maybe_arm()
        elif new and "OL" in new:
            self.log("Power restored (status=%s) — cancelling shutdown timer", new)
            self._cancel()

    def _on_battery(self, entity, attribute, old, new, kwargs):
        try:
            pct = float(new)
        except (TypeError, ValueError):
            return
        if pct <= self.battery_low:
            status = self.get_state("sensor.myups_status_data") or ""
            if "OB" not in status:
                return
            self.log("Battery %.0f%% ≤ %d%% — evaluating shutdown", pct, self.battery_low)
            self._maybe_arm()

    def _on_runtime(self, entity, attribute, old, new, kwargs):
        try:
            secs = float(new)
        except (TypeError, ValueError):
            return
        if secs <= self.runtime_low:
            status = self.get_state("sensor.myups_status_data") or ""
            if "OB" not in status:
                return
            self.log("Runtime %dmin ≤ %dmin — evaluating shutdown", int(secs), self.runtime_low)
            self._maybe_arm()

    def _on_test_event(self, event_name, data, kwargs):
        self.log("TEST MODE triggered via event '%s'", event_name)
        threading.Thread(target=self._run_tests, daemon=True).start()

    # ── arming / cancellation ────────────────────────────────────────────────

    def _maybe_arm(self):
        with self._lock:
            if self._in_progress:
                return

            status  = self.get_state("sensor.myups_status_data") or "unknown"
            on_batt = "OB" in status

            try:
                battery = float(self.get_state("sensor.myups_battery_charge") or 100)
            except ValueError:
                battery = 100

            try:
                runtime = float(self.get_state("sensor.ups_estimated_runtime") or 9999)
            except ValueError:
                runtime = 9999

            if not on_batt:
                self.log("Power present (status=%s) — not arming", status)
                return

            if battery > self.battery_low and runtime > self.runtime_low:
                self.log("Levels OK (battery=%.0f%% runtime=%dmin) — not arming", battery, runtime)
                return

            if self._timer is not None:
                return

            self.log(
                "ARMING shutdown in %ds (battery=%.0f%% runtime=%dmin status=%s)",
                self.pre_delay, battery, runtime, status,
            )
            self._timer = self.run_in(self._fire, self.pre_delay)

    def _cancel(self):
        with self._lock:
            if self._timer is not None:
                self.cancel_timer(self._timer)
                self._timer = None
                self.log("Shutdown timer cancelled — power restored")

    def _fire(self, kwargs):
        with self._lock:
            self._timer = None
            status = self.get_state("sensor.myups_status_data") or ""
            if "OB" not in status:
                self.log("Power restored before shutdown fired (status=%s) — aborting", status)
                return
            self._in_progress = True

        self.log("Shutdown sequence commencing")
        threading.Thread(target=self._sequence, daemon=True).start()

    # ── SSH helpers ─────────────────────────────────────────────────────────

    def _resolve_key(self, key_path):
        """A bare filename is resolved relative to this script's own directory
        (the apps/ folder), since the container-internal path to that folder
        varies by add-on and isn't worth hardcoding. Already-absolute paths
        pass through unchanged."""
        if key_path and not os.path.isabs(key_path):
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), key_path)
        return key_path

    def _ssh_connect(self, ip, user, password, key_path=None):
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if key_path:
            c.connect(ip, username=user, key_filename=self._resolve_key(key_path),
                      timeout=self.ssh_timeout, look_for_keys=False, allow_agent=False)
        else:
            c.connect(ip, username=user, password=password,
                      timeout=self.ssh_timeout, look_for_keys=False, allow_agent=False)
        return c

    def _ssh_run(self, ip, user, password, cmd, timeout=60, key_path=None):
        """Execute cmd via SSH (key auth if key_path given, else password). Returns (rc, stdout, stderr)."""
        try:
            c = self._ssh_connect(ip, user, password, key_path=key_path)
            _, stdout, stderr = c.exec_command(cmd, timeout=timeout)
            out = stdout.read().decode().strip()
            err = stderr.read().decode().strip()
            rc  = stdout.channel.recv_exit_status()
            c.close()
            return rc, out, err
        except Exception as exc:
            return -1, "", str(exc)

    def _ssh_via_jump(self, jump_ip, jump_user, jump_pass,
                      target_ip, target_user, cmd, timeout=60, key_path=None):
        """Run cmd on target_ip via a nested SSH from the jump host."""
        wrapped = (
            f"ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "
            f"{target_user}@{target_ip} '{cmd}'"
        )
        return self._ssh_run(jump_ip, jump_user, jump_pass, wrapped, timeout=timeout + 15, key_path=key_path)

    # ── Proxmox API helpers ──────────────────────────────────────────────────

    def _pve_auth(self, pve_ip, api_user, api_pass):
        """Authenticate and return (auth_headers, auth_cookies)."""
        r = requests.post(
            f"https://{pve_ip}:8006/api2/json/access/ticket",
            data={"username": api_user, "password": api_pass},
            verify=False, timeout=15,
        )
        r.raise_for_status()
        d = r.json()["data"]
        return (
            {"CSRFPreventionToken": d["CSRFPreventionToken"]},
            {"PVEAuthCookie": d["ticket"]},
        )

    def _pve_find_vm(self, pve_ip, vm_name, headers, cookies):
        """
        Find a VM by name using the cluster resources API.
        Returns the VM dict (includes 'node', 'vmid', 'status') or None.
        Works for both clustered and standalone Proxmox.
        """
        r = requests.get(
            f"https://{pve_ip}:8006/api2/json/cluster/resources",
            params={"type": "vm"},
            headers=headers, cookies=cookies, verify=False, timeout=15,
        )
        r.raise_for_status()
        return next((v for v in r.json().get("data", []) if v.get("name", "").lower() == vm_name.lower()), None)

    def _pve_shutdown_vm(self, pve_ip, node, vmid, headers, cookies):
        """Issue an ACPI shutdown to a specific VM."""
        requests.post(
            f"https://{pve_ip}:8006/api2/json/nodes/{node}/qemu/{vmid}/status/shutdown",
            headers=headers, cookies=cookies,
            data={"forceStop": 0, "timeout": 120},
            verify=False, timeout=15,
        ).raise_for_status()

    # ── Proxmox VM shutdown (by name) ────────────────────────────────────────

    def _proxmox_shutdown_vm(self, pve_ip, vm_name, api_user, api_pass):
        try:
            headers, cookies = self._pve_auth(pve_ip, api_user, api_pass)
            vm = self._pve_find_vm(pve_ip, vm_name, headers, cookies)
            if vm is None:
                self.log("VM '%s' not found via %s — skipping", vm_name, pve_ip, level="WARNING")
                return
            if vm.get("status") == "stopped":
                self.log("VM %s already stopped", vm_name)
                return
            self._pve_shutdown_vm(pve_ip, vm["node"], vm["vmid"], headers, cookies)
            self.log("Proxmox ACPI shutdown issued: %s (node=%s vmid=%s)",
                     vm_name, vm["node"], vm["vmid"])
        except Exception as exc:
            self.log("Proxmox API %s / VM '%s' failed: %s", pve_ip, vm_name, exc, level="WARNING")

    # ── Proxmox VM shutdown (by vmid — used for HAOS VM) ────────────────────

    def _proxmox_shutdown_haos(self, pve_ip, haos_vmid, api_user, api_pass):
        """
        Shut down the HAOS VM by its numeric ID.  AppDaemon runs inside this VM,
        so this call schedules our own eventual termination.
        """
        try:
            headers, cookies = self._pve_auth(pve_ip, api_user, api_pass)
            # Resolve node name from cluster resources
            r = requests.get(
                f"https://{pve_ip}:8006/api2/json/cluster/resources",
                params={"type": "vm"},
                headers=headers, cookies=cookies, verify=False, timeout=15,
            )
            r.raise_for_status()
            vm = next((v for v in r.json().get("data", [])
                       if str(v.get("vmid")) == str(haos_vmid)), None)
            node = vm["node"] if vm else "pve"  # fall back to "pve" if lookup fails
            self._pve_shutdown_vm(pve_ip, node, haos_vmid, headers, cookies)
            self.log("ACPI shutdown issued to HAOS VM %s (node=%s) — "
                     "AppDaemon will be terminated when VM stops", haos_vmid, node)
        except Exception as exc:
            self.log("HAOS VM shutdown failed: %s — proceeding anyway", exc, level="WARNING")

    # ── Synology NAS API ────────────────────────────────────────────────────

    def _synology_login(self, nas_ip, nas_user, nas_pass):
        """Return session ID, or raise on failure."""
        r = requests.get(
            f"http://{nas_ip}:5000/webapi/auth.cgi",
            params={
                "api":     "SYNO.API.Auth",
                "version": "3",
                "method":  "login",
                "account": nas_user,
                "passwd":  nas_pass,
                "session": "Core",
                "format":  "sid",
            },
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        if not data.get("success"):
            raise RuntimeError(f"Synology login failed: {data.get('error')}")
        return data["data"]["sid"]

    def _synology_logout(self, nas_ip, sid):
        try:
            requests.get(
                f"http://{nas_ip}:5000/webapi/auth.cgi",
                params={"api": "SYNO.API.Auth", "version": "1",
                        "method": "logout", "session": "Core", "_sid": sid},
                timeout=10,
            )
        except Exception:
            pass

    def _synology_shutdown(self, nas_ip, nas_user, nas_pass):
        """Login to Synology DSM and issue a system shutdown."""
        try:
            sid = self._synology_login(nas_ip, nas_user, nas_pass)
            r = requests.post(
                f"http://{nas_ip}:5000/webapi/entry.cgi",
                data={"api": "SYNO.Core.System", "version": "1",
                      "method": "shutdown", "_sid": sid},
                timeout=15,
            )
            r.raise_for_status()
            result = r.json()
            if result.get("success"):
                self.log("Synology NAS %s shutdown initiated — will power off in ~2-3 min", nas_ip)
            else:
                self.log("Synology shutdown returned: %s", result, level="WARNING")
        except Exception as exc:
            self.log("Synology NAS %s shutdown failed: %s", nas_ip, exc, level="WARNING")

    def _synology_get_info(self, nas_ip, nas_user, nas_pass):
        """
        Login, read DSM system info (read-only), logout.
        Returns a human-readable summary string, or raises on failure.
        """
        sid = self._synology_login(nas_ip, nas_user, nas_pass)
        try:
            r = requests.get(
                f"http://{nas_ip}:5000/webapi/entry.cgi",
                params={"api": "SYNO.DSM.Info", "version": "2",
                        "method": "getinfo", "_sid": sid},
                timeout=15,
            )
            r.raise_for_status()
            d = r.json().get("data", {})
            return (
                f"model={d.get('model','?')}  "
                f"DSM={d.get('version','?')}  "
                f"uptime={d.get('uptime','?')}s"
            )
        finally:
            self._synology_logout(nas_ip, sid)

    # ── kubectl drain (via jump host → master) ───────────────────────────────

    def _drain(self, node_name):
        jump   = self.args["jump_host"]
        k_ip   = self.args.get("kubectl_ip",   "10.0.50.102")
        k_user = self.args.get("kubectl_user", "ubuntu")
        cmd = (
            f"kubectl drain {node_name}"
            f" --ignore-daemonsets --delete-emptydir-data"
            f" --grace-period=30 --timeout={self.drain_timeout}s --force"
        )
        self.log("Draining %s (jump→%s→%s)", node_name, jump["ip"], k_ip)
        rc, out, err = self._ssh_via_jump(
            jump["ip"], jump["user"], jump["pass"],
            k_ip, k_user, cmd, timeout=self.drain_timeout,
            key_path=jump.get("key_path"),
        )
        if rc == 0:
            self.log("Node %s drained", node_name)
        else:
            self.log("Drain %s rc=%d %s — continuing", node_name, rc, err or out, level="WARNING")

    # ── test mode ────────────────────────────────────────────────────────────

    def _run_tests(self):
        """
        Exercises every connection path with read-only commands only.
        Fire via HA Developer Tools → Events → Event type: ups_shutdown_test
        Results appear in the AppDaemon log.
        """
        nodes         = self.args.get("k3s_nodes",       [])
        proxmox_hosts = self.args.get("proxmox_hosts",   [])
        pve_api_user  = self.args.get("proxmox_api_user", "root@pam")
        pve_api_pass  = self.args.get("proxmox_api_pass", "")
        intel_ip      = self.args.get("intel_ip",         "10.0.0.71")
        intel_user    = self.args.get("intel_user",       "root")
        intel_pass    = self.args.get("intel_pass",       "")
        haos_vmid     = self.args.get("haos_vmid",        100)
        nas_ip        = self.args.get("nas_ip",           "10.0.50.35")
        nas_user      = self.args.get("nas_user",         "davidb")
        nas_pass      = self.args.get("nas_pass",         "")
        jump          = self.args["jump_host"]
        k_ip          = self.args.get("kubectl_ip",   "10.0.50.102")
        k_user        = self.args.get("kubectl_user", "ubuntu")

        workers = [n for n in nodes if n.get("role") == "worker"]
        masters = [n for n in nodes if n.get("role") == "master"]

        passed = 0
        failed = 0

        def ok(label, detail=""):
            nonlocal passed
            passed += 1
            self.log("  PASS  %s%s", label, f"  — {detail}" if detail else "")

        def fail(label, detail=""):
            nonlocal failed
            failed += 1
            self.log("  FAIL  %s%s", label, f"  — {detail}" if detail else "", level="WARNING")

        self.log("=" * 60)
        self.log("UPS SHUTDOWN TEST — read-only connectivity check")
        self.log("=" * 60)

        # ── [1] Jump host ────────────────────────────────────────────────
        self.log("[1/7] Jump host SSH  %s@%s", jump["user"], jump["ip"])
        rc, out, err = self._ssh_run(
            jump["ip"], jump["user"], jump["pass"], "hostname && uptime",
            key_path=jump.get("key_path"),
        )
        if rc == 0:
            ok(f"jump {jump['ip']}", out.replace("\n", " | "))
        else:
            fail(f"jump {jump['ip']}", err or out)

        # ── [2] Jump → master kubectl ────────────────────────────────────
        self.log("[2/7] Jump → master kubectl  %s@%s via %s", k_user, k_ip, jump["ip"])
        rc, out, err = self._ssh_via_jump(
            jump["ip"], jump["user"], jump["pass"],
            k_ip, k_user, "kubectl get nodes -o wide --no-headers",
            key_path=jump.get("key_path"),
        )
        if rc == 0:
            for line in out.splitlines():
                self.log("      %s", line)
            ok(f"kubectl get nodes via {jump['ip']}→{k_ip}")
        else:
            fail(f"kubectl via jump → {k_ip}", err or out)

        # ── [3] Worker direct SSH ────────────────────────────────────────
        self.log("[3/7] Worker SSH")
        for n in workers:
            rc, out, err = self._ssh_run(
                n["ip"], n["user"], n["pass"], "hostname && uptime",
                key_path=n.get("key_path"),
            )
            if rc == 0:
                ok(f"worker {n['node_name']} ({n['ip']})", out.replace("\n", " | "))
            else:
                fail(f"worker {n['node_name']} ({n['ip']})", err or out)

        # ── [4] Proxmox API — find master VMs ───────────────────────────
        self.log("[4/7] Proxmox API — locate master VMs")
        pve_sessions = {}
        for n in masters:
            pve_ip = n.get("pve_host", "")
            if not pve_ip:
                fail(f"master {n['node_name']}", "no pve_host configured")
                continue
            try:
                if pve_ip not in pve_sessions:
                    pve_sessions[pve_ip] = self._pve_auth(pve_ip, pve_api_user, pve_api_pass)
                headers, cookies = pve_sessions[pve_ip]
                vm = self._pve_find_vm(pve_ip, n["node_name"], headers, cookies)
                if vm:
                    ok(
                        f"master {n['node_name']} on pve {pve_ip}",
                        f"node={vm['node']} vmid={vm['vmid']} "
                        f"status={vm.get('status','?')} "
                        f"mem={vm.get('mem', 0) // 1024 // 1024}MB",
                    )
                else:
                    fail(f"master {n['node_name']} on pve {pve_ip}", "VM not found")
            except Exception as exc:
                fail(f"Proxmox API {pve_ip} / {n['node_name']}", str(exc))

        # ── [5] Proxmox host direct SSH ──────────────────────────────────
        self.log("[5/7] Proxmox host SSH")
        for pve in proxmox_hosts:
            rc, out, err = self._ssh_run(
                pve["ip"], pve["user"], pve["pass"],
                "pveversion 2>/dev/null || (hostname && uname -r)",
            )
            if rc == 0:
                ok(f"pve {pve['ip']}", out.replace("\n", " | "))
            else:
                fail(f"pve {pve['ip']}", err or out)

        # ── [6] intel_sbc — SSH + locate HAOS VM ─────────────────────────
        self.log("[6/7] intel_sbc SSH + HAOS VM lookup  %s@%s", intel_user, intel_ip)
        rc, out, err = self._ssh_run(intel_ip, intel_user, intel_pass, "hostname && uptime")
        if rc == 0:
            ok(f"intel_sbc SSH {intel_ip}", out.replace("\n", " | "))
        else:
            fail(f"intel_sbc SSH {intel_ip}", err or out)

        try:
            headers, cookies = self._pve_auth(intel_ip, pve_api_user, intel_pass)
            r = requests.get(
                f"https://{intel_ip}:8006/api2/json/cluster/resources",
                params={"type": "vm"},
                headers=headers, cookies=cookies, verify=False, timeout=15,
            )
            r.raise_for_status()
            haos_vm = next(
                (v for v in r.json().get("data", []) if str(v.get("vmid")) == str(haos_vmid)),
                None,
            )
            if haos_vm:
                ok(
                    f"HAOS VM {haos_vmid} on intel_sbc",
                    f"node={haos_vm['node']} name={haos_vm.get('name','?')} "
                    f"status={haos_vm.get('status','?')}",
                )
            else:
                fail(f"HAOS VM {haos_vmid} on intel_sbc", "VM not found — check haos_vmid in apps.yaml")
        except Exception as exc:
            fail(f"intel_sbc Proxmox API", str(exc))

        # ── [7] Synology NAS ──────────────────────────────────────────────
        self.log("[7/7] Synology NAS  %s  user=%s", nas_ip, nas_user)
        try:
            info = self._synology_get_info(nas_ip, nas_user, nas_pass)
            ok(f"NAS {nas_ip}", info)
        except Exception as exc:
            fail(f"NAS {nas_ip}", str(exc))

        # ── summary ──────────────────────────────────────────────────────
        total = passed + failed
        self.log("=" * 60)
        if failed == 0:
            self.log("TEST COMPLETE — %d/%d passed  ✓  ready for real shutdown", passed, total)
        else:
            self.log(
                "TEST COMPLETE — %d/%d passed, %d FAILED  ✗  fix failures before relying on shutdown",
                passed, total, failed, level="WARNING",
            )
        self.log("=" * 60)

    # ── shutdown sequence ────────────────────────────────────────────────────

    def _sequence(self):
        nodes         = self.args.get("k3s_nodes",        [])
        proxmox_hosts = self.args.get("proxmox_hosts",    [])
        pve_api_user  = self.args.get("proxmox_api_user", "root@pam")
        pve_api_pass  = self.args.get("proxmox_api_pass", "")
        intel_ip      = self.args.get("intel_ip",         "10.0.0.71")
        intel_user    = self.args.get("intel_user",       "root")
        intel_pass    = self.args.get("intel_pass",       "")
        haos_vmid     = self.args.get("haos_vmid",        100)
        nas_ip        = self.args.get("nas_ip",           "10.0.50.35")
        nas_user      = self.args.get("nas_user",         "davidb")
        nas_pass      = self.args.get("nas_pass",         "")

        workers = [n for n in nodes if n.get("role") == "worker"]
        masters = [n for n in nodes if n.get("role") == "master"]

        # ── 1. Drain workers ──────────────────────────────────────────────
        self.log("Step 1/6 — draining worker nodes")
        for n in workers:
            self._drain(n["node_name"])

        # ── 2. Drain masters (all but last) ───────────────────────────────
        self.log("Step 2/6 — draining non-final master nodes")
        for n in masters[:-1]:
            self._drain(n["node_name"])

        # ── 3. Halt workers via SSH ───────────────────────────────────────
        self.log("Step 3/6 — halting worker nodes")
        for n in workers:
            self.log("Halting worker %s (%s)", n["node_name"], n["ip"])
            self._ssh_run(n["ip"], n["user"], n["pass"], "sudo shutdown -h now",
                          key_path=n.get("key_path"))
        time.sleep(20)

        # ── 4. Halt masters via Proxmox API ──────────────────────────────
        self.log("Step 4/6 — halting master VMs via Proxmox API")
        for n in masters:
            pve_ip = n.get("pve_host", "")
            if not pve_ip:
                self.log("No pve_host for %s — skipping", n["node_name"], level="WARNING")
                continue
            self._proxmox_shutdown_vm(pve_ip, n["node_name"], pve_api_user, pve_api_pass)
        time.sleep(60)

        # ── 5. Halt Proxmox hosts via SSH ─────────────────────────────────
        self.log("Step 5/6 — halting Proxmox hosts")
        for pve in proxmox_hosts:
            self.log("Halting Proxmox %s", pve["ip"])
            self._ssh_run(pve["ip"], pve["user"], pve["pass"], "shutdown -h now")
        time.sleep(20)

        # ── 6. intel_sbc + NAS — order matters ───────────────────────────
        self.log("Step 6/6 — shutting down intel_sbc and NAS")

        # 6a. Schedule a delayed OS shutdown on intel_sbc so it powers off automatically
        #     after the HAOS VM has finished its graceful shutdown (~90s).
        self.log("Scheduling intel_sbc host OS shutdown in 5 minutes")
        self._ssh_run(intel_ip, intel_user, intel_pass, "shutdown -h +5")

        # 6b. Send ACPI shutdown to the HAOS VM.  AppDaemon runs inside it and will
        #     be terminated when the VM completes its graceful shutdown (~90s from now).
        self.log("Sending ACPI shutdown to HAOS VM %s on intel_sbc", haos_vmid)
        self._proxmox_shutdown_haos(intel_ip, haos_vmid, pve_api_user, intel_pass)

        # 6c. Shut down the NAS while AppDaemon is still alive (HAOS is still shutting
        #     down).  The NAS takes 2-3 min to power off — intel_sbc only goes down at
        #     +5 min — so the NAS remains accessible throughout intel_sbc's shutdown.
        self.log("Initiating Synology NAS %s shutdown — NAS stays up while intel_sbc winds down",
                 nas_ip)
        self._synology_shutdown(nas_ip, nas_user, nas_pass)

        # Brief pause so the NAS API request is processed before we're killed.
        time.sleep(10)

        # AppDaemon will be terminated when the HAOS VM completes shutdown.
        # intel_sbc host powers off automatically at the +5 min mark.
        # NAS completes its own shutdown in ~2-3 min, after intel_sbc is already down.
        self.log("Shutdown sequence complete — waiting for HAOS VM to stop this process")
