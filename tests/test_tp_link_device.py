import os
import pytest

from tplinkcloud import TPLinkDeviceManager


@pytest.fixture(scope='module')
def client():
    return TPLinkDeviceManager(
        username=os.environ.get('TPLINK_KASA_USERNAME'),
        password=os.environ.get('TPLINK_KASA_PASSWORD'),
        prefetch=False,
        cache_devices=False,
        tplink_cloud_api_host=os.environ.get('TPLINK_KASA_API_URL'),
        verbose=True,
        term_id=os.environ.get('TPLINK_KASA_TERM_ID')
    )


@pytest.mark.usefixtures('client')
class TestTPLinkDevice(object):

    def test_get_net_info_gets_net_info(self, client):
        device_name = 'Left Lamp'
        device = client.find_device(device_name)
        net_info = device.get_net_info()

        assert net_info is not None
        assert net_info.ssid == "My WiFi Network"
        assert net_info.key_type == 3
        assert net_info.rssi == -39
        assert net_info.err_code == 0
