import re
from osbot_utils.type_safe.primitives.core.Safe_Str                                 import Safe_Str
from osbot_utils.type_safe.primitives.core.enums.Enum__Safe_Str__Regex_Mode         import Enum__Safe_Str__Regex_Mode
from osbot_utils.type_safe.primitives.domains.network.safe_str.Safe_Str__IP_Address import Safe_Str__IP_Address

TYPE_SAFE_STR__URL__HOST__MAX_LENGTH = 253                                          # RFC 1035 max domain name length
TYPE_SAFE_STR__URL__HOST__REGEX      = re.compile(r'^[a-zA-Z0-9.\-]+$')             # permissive first pass — structural checks in __new__


class Safe_Str__Url__Host(Safe_Str):                                                # hostname: domain name or IP address (no scheme, port, or path)
    """
    Safe string class for URL host component (domain or IP address only).

    Valid:
    - "localhost"
    - "example.com"
    - "api.sgraph.ai"
    - "192.168.1.1"
    - "127.0.0.1"

    Invalid:
    - "http://example.com"   (has scheme)
    - "example.com:8080"     (has port)
    - "example.com/path"     (has path)
    - "256.1.1.1"            (invalid IP)
    - ""                     (empty allowed by default)
    """
    regex             = TYPE_SAFE_STR__URL__HOST__REGEX
    regex_mode        = Enum__Safe_Str__Regex_Mode.MATCH
    max_length        = TYPE_SAFE_STR__URL__HOST__MAX_LENGTH
    trim_whitespace   = True
    strict_validation = True
    allow_empty       = True

    def __new__(cls, value=None):
        if value is None or value == '':
            return super().__new__(cls, value)                                      # allow empty if permitted

        instance = super().__new__(cls, value)                                      # regex validation first
        cls._validate_host(str(instance))                                           # then structural validation
        return instance

    @classmethod
    def _validate_host(cls, host):                                                  # validate host is a domain or IP
        if not host:
            return

        if '://' in host:                                                           # reject if scheme present
            raise ValueError(f"Host must not contain a scheme: '{host}'")

        if ':' in host and not cls._is_ipv6(host):                                  # reject if port present (but allow IPv6)
            raise ValueError(f"Host must not contain a port: '{host}'")

        if '/' in host:                                                             # reject if path present
            raise ValueError(f"Host must not contain a path: '{host}'")

        if cls._is_ip_like(host):                                                   # looks like an IP — validate as IP
            try:
                Safe_Str__IP_Address(host)
                return                                                              # valid IP
            except (ValueError, TypeError):
                raise ValueError(f"Invalid IP address: '{host}'") from None

        if not cls._is_valid_domain(host):                                          # not IP-like — validate as domain
            raise ValueError(f"Invalid hostname: '{host}' is neither a valid IP address nor domain name")

    @classmethod
    def _is_ip_like(cls, host):                                                     # all-numeric labels = IP attempt
        if not host:
            return False
        labels = host.split('.')
        return all(label.isdigit() for label in labels if label)

    @classmethod
    def _is_ipv6(cls, host):                                                        # rough check for IPv6 (contains multiple colons)
        return host.count(':') > 1

    @classmethod
    def _is_valid_domain(cls, domain):                                              # RFC 1035 domain validation
        if not domain or len(domain) > 253:
            return False
        if domain == 'localhost':
            return True
        labels = domain.split('.')
        if not labels:
            return False
        for label in labels:
            if not label or len(label) > 63:
                return False
            if label.startswith('-') or label.endswith('-'):
                return False
            if not re.match(r'^[a-zA-Z0-9\-]+$', label):
                return False
        return True