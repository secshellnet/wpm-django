import requests
from django.db.models.signals import post_save
from django.dispatch import receiver

from wpm.models import Peer


@receiver(post_save, sender=Peer)
def add_peer_handler(sender, instance: Peer, **kwargs):
    # the flag _skip_api_call can be used to prevent triggering
    # an infinite loop when saving the instance inside the post_save signal handler
    # also when updated by the check_valid function and deleting the peer, this flag is being used
    if hasattr(instance, '_skip_api_call'):
        return

    instance._skip_api_call = True

    # prevent creation of peers, if user has no first / lastname set
    # the save_model method shouldn't even create the object,
    # so this signal handler should have never been invoked
    if not instance.owner.first_name or not instance.owner.last_name:
        print(f"SIGNAL HANDLER: Unable to create peer for {instance.owner}, has no real name configured!")
        return

    requests.post(
        f"http://{instance.endpoint.name}:{instance.endpoint.wpm_api_port}/api/peer/",
        headers={
            "Authorization": f"Bearer {instance.endpoint.wpm_api_token}",
        },
        json={
            "userIdentifier": f"{instance.owner.first_name.upper()}-{instance.owner.last_name.upper()}",
            "peerIdentifier": instance.name,
            "publicKey": instance.public_key,
            "psk": instance.psk,
            "tunnelIpv4": instance.tunnel_ipv4,
            "tunnelIpv6": instance.tunnel_ipv6,
        },
    )
    instance.last_action = Peer.Action.CREATED
    instance.save()

    del instance._skip_api_call


def delete_handler(instance: Peer):
    # mark instance for deletion
    instance.valid = False
    instance.last_action = Peer.Action.DELETED
    instance._skip_api_call = True
    instance.save()
    del instance._skip_api_call

    identifier = f"{instance.owner.first_name.upper()}-{instance.owner.last_name.upper()}-{instance.name}"
    requests.delete(
        f"http://{instance.endpoint.name}:{instance.endpoint.wpm_api_port}/api/peer/{identifier}",
        headers={
            "Authorization": f"Bearer {instance.endpoint.wpm_api_token}",
        },
    )
