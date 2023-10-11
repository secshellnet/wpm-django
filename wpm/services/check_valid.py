import requests

from wpm.models import Peer


def check_valid():
    for peer in Peer.objects.filter(valid=False).all():
        identifier = f"{peer.owner.first_name.upper()}-{peer.owner.last_name.upper()}-{peer.name}"
        resp = requests.get(
            f"http://{peer.endpoint.name}:{peer.endpoint.wpm_api_port}/api/peer/{identifier}",
            headers={
                "Authorization": f"Bearer {peer.endpoint.wpm_api_token}",
            },
        )

        if resp.status_code != 200:
            print(f"WPM-API on {peer.endpoint.name} responded with HTTP status {resp.status_code}")
            return

        if peer.last_action == Peer.Action.CREATED and resp.json().get("StatusResponse").get("valid"):
            peer.valid = True
            peer._skip_api_call = True
            peer.save()
            del peer._skip_api_call

        if peer.last_action == Peer.Action.DELETED and not resp.json().get("StatusResponse").get("valid"):
            peer.delete()
