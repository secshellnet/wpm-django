from django.contrib import admin
from django.forms import CharField, ModelForm, Textarea, TextInput, BooleanField
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Peer, WireguardEndpoint, DNSServer
from .signals import delete_handler

WG_CONFIG = """# Secure Shell Networks: {gateway}

[Interface]
PrivateKey = ### PRIVATE KEY ###
Address = {addresses}
DNS = {dns}

[Peer]
PublicKey = b5V840pvHj0JPyjh6IAvEtIaEK0XNsabssvk6iNEpDc=
Endpoint = {endpoint}
AllowedIPs = 0.0.0.0/0,::/0
PersistentKeepalive = 30
"""


class NewPeerAdminForm(ModelForm):
    """
    form to create new peers
    """
    model = Peer
    private_key = CharField(
        required=False, help_text=_("This key has been generated in the browser."
                                    "Feel free to overwrite the public key below to use your own key."))
    configure_psk = BooleanField(required=False, label=_("configure psk"))

    class Meta:
        model = Peer
        fields = ("endpoint", "name", "private_key", "public_key", "configure_psk", "psk",)
        widgets = {
            "name": TextInput(attrs={'size': 45}),
            "private_key": TextInput(attrs={'size': 45}),
            "public_key": TextInput(attrs={'size': 45}),
            "psk": TextInput(attrs={'size': 45}),
        }

    class Media:
        js = ("admin/js/wireguard.js", "admin/js/wireguard_add_peer.js", )


class PeerAdminForm(ModelForm):
    """
    form to create new peers
    """
    model = Peer
    config = CharField(widget=Textarea(attrs={'rows': 16, 'cols': 100}), required=False)

    class Meta:
        model = Peer
        fields = ("endpoint", "name", "tunnel_ipv4", "tunnel_ipv6", "public_key", "psk", "config")

    class Media:
        js = ("admin/js/wireguard_show_peer.js", )

    def __init__(self, *args, **kwargs):
        super(PeerAdminForm, self).__init__(*args, **kwargs)
        # set all fields to read only / disabled, so they are being displayed as paragraph
        for field in self.Meta.fields:
            self.fields[field].disabled = True


@admin.register(Peer)
class PeerAdmin(admin.ModelAdmin):

    class Media:
        css = {
            "all": ("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",)
        }
        js = ("admin/js/wireguard_overview.js",)

    list_display_links = ("name", "tunnel_ips")

    def valid_color(self, obj):
        color = "#4cb34c" if obj.valid else "#e50a0a"
        return format_html(f'<i class="fa-solid fa-circle" style="color: {color}"></i>')
    valid_color.short_description = _("valid")

    def get_list_display(self, request):
        if request.user.is_superuser:
            return "owner", "endpoint", "name", "tunnel_ips", "valid_color",
        return "endpoint", "name", "tunnel_ips", "valid_color",

    def get_list_filter(self, request):
        if request.user.is_superuser:
            return "owner", "valid", "endpoint",
        return "valid", "endpoint",

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.owner = request.user

            # prevent creation of peers, if user has no first / lastname set
            if not obj.owner.first_name or not obj.owner.last_name:
                print(f"Unable to create peer for {obj.owner}, has no real name configured!")
                return

        super().save_model(request, obj, form, change)

    def get_form(self, request, obj: Peer = None, **kwargs):
        # when the peer doesn't exist yet, we show the formular
        # where the user can choose a name and whether a psk should be configured
        if not obj:
            form = NewPeerAdminForm
        else:
            # otherwise we use the PeerAdminForm which includes a config field
            form = PeerAdminForm
            form.base_fields["config"].initial = WG_CONFIG.format(**{
                "gateway": obj.endpoint.name,
                "addresses": obj.tunnel_ips(),
                "endpoint": f"{obj.endpoint.endpoint_ip}:{obj.endpoint.endpoint_port}",
                "dns": ','.join([dns.ip_address for dns in obj.endpoint.dns_server.all()]),
            })

        return form

    def has_delete_permission(self, request, obj: Peer = None):
        # invalid objects can't be deleted for asynchronous reasons
        if obj:
            return obj.valid
        return False

    def delete_model(self, request, obj):
        delete_handler(obj)


@admin.register(WireguardEndpoint)
class WireguardEndpointAdmin(admin.ModelAdmin):
    list_display = ("name", "ipv4_net", "ipv6_net", "endpoint_ip", "endpoint_port", "public_key", "wpm_api_port",)
    list_display_links = ("name", "ipv4_net", "ipv6_net", "endpoint_ip", "endpoint_port", "public_key",)


@admin.register(DNSServer)
class DNSServerAdmin(admin.ModelAdmin):
    list_display = ("ip_address",)
