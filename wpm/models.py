from ipaddress import IPv4Network, IPv4Address, IPv6Address, IPv6Network
from random import randint

from django.conf import settings
from django.core.validators import RegexValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class DNSServer(models.Model):

    class Meta:
        verbose_name = _("dns server")
        verbose_name_plural = _("dns servers")

    ip_address = models.GenericIPAddressField(_("ip address"))

    def __str__(self):
        return self.ip_address


class WireguardEndpoint(models.Model):

    class Meta:
        verbose_name = _("wireguard endpoint")
        verbose_name_plural = _("wireguard endpoints")

    name = models.CharField(max_length=255, unique=True, validators=[
        RegexValidator(
            regex=r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            message='Name must be a fully qualified domain name.',
        )
    ])

    ipv4_net = models.CharField(max_length=15, validators=[
        RegexValidator(
            regex=r'^\d+\.\d+\.\d+\.\d+/\d+$',
            message='IPv4 network must be in CIDR notation, e.g., "192.168.0.0/24".',
        ),
    ])
    ipv6_net = models.CharField(max_length=39, null=True, blank=True, validators=[
        RegexValidator(
            regex=r'^[0-9a-fA-F:/]+$',
            message='IPv6 network must be in CIDR notation, e.g., "2001:0db8::/32".',
        ),
    ])

    endpoint_ip = models.GenericIPAddressField()
    endpoint_port = models.PositiveIntegerField(validators=[MaxValueValidator(65535)])
    dns_server = models.ManyToManyField(DNSServer)

    public_key = models.CharField(_("public key"), max_length=44, validators=[
        RegexValidator(
            regex=r'^[A-Za-z0-9+/]{43}=$',
            message="Invalid wireguard public key."
        )
    ])

    wpm_api_token = models.CharField(_("api token"), max_length=64)
    wpm_api_port = models.PositiveIntegerField(validators=[MaxValueValidator(65535)])

    def __str__(self):
        return self.name


class Peer(models.Model):

    class Meta:
        verbose_name = _("peer")
        verbose_name_plural = _("peers")

        # ensure each peer is unique for the scope of the endpoint
        unique_together = ("name", "endpoint",)

    class Action(models.IntegerChoices):
        CREATED = 0, _("created")
        DELETED = 1, _("deleted")

    endpoint = models.ForeignKey(WireguardEndpoint, on_delete=models.CASCADE, verbose_name=_("wireguard endpoint"))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("owner"))
    name = models.CharField(_("name"), max_length=32, validators=[
        RegexValidator(
            regex=r'^[A-Za-z0-9]{1,32}$',
            message="Only upper/lowercase letters and numbers. Up to 32 characters allowed."
        )
    ])
    tunnel_ipv4 = models.GenericIPAddressField(_("tunnel ipv4"), unique=True)
    tunnel_ipv6 = models.GenericIPAddressField(_("tunnel ipv6"), unique=True)
    public_key = models.CharField(_("public key"), max_length=44, validators=[
        RegexValidator(
            regex=r'^[A-Za-z0-9+/]{43}=$',
            message="Invalid wireguard public key."
        )
    ])
    psk = models.CharField(_("psk"), max_length=44, default=None, null=True, blank=True, validators=[
        RegexValidator(
            regex=r'^[A-Za-z0-9+/]{43}=$',
            message="Invalid wireguard psk."
        )
    ])
    created = models.DateTimeField(_("created"), default=timezone.now)
    valid = models.BooleanField(_("valid"), default=False)

    last_action = models.IntegerField(_("last_action"), choices=Action.choices, default=Action.CREATED)

    def save(self, *args, **kwargs):
        if self.pk:
            return super(Peer, self).save(*args, **kwargs)

        # generate ipv4 tunnel address: get all ipv4 addresses (vyos is using the first address)
        all_addresses = list(IPv4Network(self.endpoint.ipv4_net).hosts())[1:]
        used_addresses = set(IPv4Address(p.tunnel_ipv4) for p in Peer.objects.filter(endpoint=self.endpoint).all())
        self.tunnel_ipv4 = str(next(addr for addr in all_addresses if addr not in used_addresses))

        # generate ipv6 tunnel address: get all ipv4 addresses (vyos is using the first address)
        used_addresses6 = [IPv6Address(p.tunnel_ipv6) for p in Peer.objects.filter(endpoint=self.endpoint).all()]
        used_addresses6.append(next(IPv6Network(self.endpoint.ipv6_net).hosts()))

        def _get_random():
            # Which of the network.num_addresses we want to select?
            addr_no = randint(0, IPv6Network(self.endpoint.ipv6_net).num_addresses)
            # Create the random address by converting to a 128-bit integer, adding addr_no and converting back
            network_int = int.from_bytes(IPv6Network(self.endpoint.ipv6_net).network_address.packed, byteorder="big")
            addr_int = network_int + addr_no
            return IPv6Address(addr_int.to_bytes(16, byteorder="big"))
        while (ipv6_addr := _get_random()) in used_addresses6:
            pass

        self.tunnel_ipv6 = str(ipv6_addr)
        super(Peer, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    def tunnel_ips(self) -> str:
        return f"{self.tunnel_ipv4}/32, {self.tunnel_ipv6}/128"
