from __future__ import annotations

import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]


class UbuntuCompatibilityTests(unittest.TestCase):
    def test_installer_accepts_both_supported_lts_releases(self) -> None:
        installer = (REPOSITORY / "install.sh").read_text(encoding="utf-8")

        self.assertIn(
            '( "${VERSION_ID:-}" != 22.04 && "${VERSION_ID:-}" != 24.04 )',
            installer,
        )
        self.assertIn("host_freerdp_package=freerdp2-x11", installer)
        self.assertIn("host_freerdp_package=freerdp3-x11", installer)
        self.assertIn('curl "$host_freerdp_package"', installer)

    def test_newer_grdctl_commands_are_feature_detected(self) -> None:
        installer = (REPOSITORY / "install.sh").read_text(encoding="utf-8")
        launcher = (
            REPOSITORY / "scripts" / "uu-remote-bridge"
        ).read_text(encoding="utf-8")

        self.assertIn("grdctl_has_rdp_command set-port", installer)
        self.assertIn(
            "grdctl_has_rdp_command disable-port-negotiation", installer
        )
        self.assertIn(
            "gnome-remote-desktop-daemon --rdp-port", launcher
        )

    def test_libei_backport_is_required_only_when_grd_links_libei(self) -> None:
        installer = (REPOSITORY / "install.sh").read_text(encoding="utf-8")
        launcher = (
            REPOSITORY / "scripts" / "uu-remote-bridge"
        ).read_text(encoding="utf-8")
        verifier = (
            REPOSITORY / "scripts" / "verify.sh"
        ).read_text(encoding="utf-8")

        needle = "Shared library: [libei.so.1]"
        for text in (installer, launcher, verifier):
            self.assertIn(needle, text)
            self.assertIn("grd_uses_libei", text)

        self.assertIn(
            'if [[ "$grd_uses_libei" == true ]]; then\n'
            '    "$repo_dir/scripts/build-libei.sh" "$libei_build"',
            installer,
        )
        self.assertIn(
            "GNOME RDP does not link libei; no keymap-FD backport is required",
            verifier,
        )

    def test_primary_docs_describe_jammy_and_noble_paths(self) -> None:
        english = (REPOSITORY / "README.md").read_text(encoding="utf-8")
        chinese = (
            REPOSITORY / "i18n" / "README.zh-Hans.md"
        ).read_text(encoding="utf-8")

        for text in (english, chinese):
            self.assertIn("22.04", text)
            self.assertIn("24.04", text)
            self.assertIn("freerdp2-x11", text)
            self.assertIn("freerdp3-x11", text)


if __name__ == "__main__":
    unittest.main()
