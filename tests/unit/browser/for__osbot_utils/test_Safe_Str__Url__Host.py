# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Safe_Str__Url__Host
# ═══════════════════════════════════════════════════════════════════════════════

import pytest
from unittest                                                import TestCase
from sg_send_qa.browser.for__osbot_utils.Safe_Str__Url__Host import Safe_Str__Url__Host


class test_Safe_Str__Url__Host(TestCase):

    # ── Valid hosts ──────────────────────────────────────────────────────────

    def test__valid__localhost(self):                                            # localhost is valid
        assert str(Safe_Str__Url__Host('localhost')) == 'localhost'

    def test__valid__domain(self):                                              # standard domain
        assert str(Safe_Str__Url__Host('example.com')) == 'example.com'

    def test__valid__subdomain(self):                                           # multi-level subdomain
        assert str(Safe_Str__Url__Host('api.sgraph.ai')) == 'api.sgraph.ai'

    def test__valid__deep_subdomain(self):                                      # deep subdomain chain
        assert str(Safe_Str__Url__Host('a.b.c.example.com')) == 'a.b.c.example.com'

    def test__valid__ipv4(self):                                                # IPv4 address
        assert str(Safe_Str__Url__Host('192.168.1.1')) == '192.168.1.1'

    def test__valid__ipv4_loopback(self):                                       # loopback IP
        assert str(Safe_Str__Url__Host('127.0.0.1')) == '127.0.0.1'

    def test__valid__hyphenated_domain(self):                                   # hyphens in labels
        assert str(Safe_Str__Url__Host('my-api.example.com')) == 'my-api.example.com'

    def test__valid__empty(self):                                               # empty string allowed
        assert str(Safe_Str__Url__Host('')) == ''

    def test__valid__single_label(self):                                        # single word hostname
        assert str(Safe_Str__Url__Host('localhost')) == 'localhost'

    # ── Invalid hosts ────────────────────────────────────────────────────────

    def test__invalid__has_scheme(self):                                        # scheme not allowed
        with pytest.raises(ValueError):
            Safe_Str__Url__Host('http://example.com')

    def test__invalid__has_port(self):                                          # port not allowed
        with pytest.raises(ValueError):
            Safe_Str__Url__Host('example.com:8080')

    def test__invalid__has_path(self):                                          # path not allowed
        with pytest.raises(ValueError):
            Safe_Str__Url__Host('example.com/api')

    def test__invalid__ip_out_of_range(self):                                   # IP octet > 255
        with pytest.raises(ValueError):
            Safe_Str__Url__Host('256.1.1.1')

    def test__invalid__ip_too_few_octets(self):                                 # only 3 octets
        with pytest.raises(ValueError):
            Safe_Str__Url__Host('1.1.1')

    def test__invalid__ip_too_many_octets(self):                                # 5 octets
        with pytest.raises(ValueError):
            Safe_Str__Url__Host('1.1.1.1.1')

    def test__invalid__label_starts_with_hyphen(self):                          # RFC 1035 violation
        with pytest.raises(ValueError):
            Safe_Str__Url__Host('-example.com')

    def test__invalid__label_ends_with_hyphen(self):                            # RFC 1035 violation
        with pytest.raises(ValueError):
            Safe_Str__Url__Host('example-.com')

    # ── Type behaviour ───────────────────────────────────────────────────────

    def test__type(self):                                                       # is a Safe_Str subclass
        host = Safe_Str__Url__Host('example.com')
        assert type(host) is Safe_Str__Url__Host

    def test__equality(self):                                                   # compares equal to plain string
        host = Safe_Str__Url__Host('localhost')
        assert host == 'localhost'

    def test__whitespace_trimmed(self):                                         # leading/trailing whitespace stripped
        host = Safe_Str__Url__Host('  example.com  ')
        assert host == 'example.com'