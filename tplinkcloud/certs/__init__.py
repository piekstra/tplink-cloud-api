"""TP-Link CA certificate chain for V2 API SSL verification."""

from importlib import resources


def get_ca_cert_path() -> str:
    """Get the filesystem path to the bundled TP-Link CA certificate chain.

    The V2 API servers (n-*.tplinkcloud.com) use TP-Link's private CA,
    which is not in the system trust store. This chain includes:
        - Root: tp-link-CA
        - Intermediate: TP-LINK CA P1
        - Leaf: *.tplinkcloud.com
    """
    ref = resources.files(__package__) / "tplink-ca-chain.pem"
    # resources.as_file extracts to a temp location if needed (e.g. from a zip)
    # but for a regular install the path is stable
    with resources.as_file(ref) as path:
        return str(path)
