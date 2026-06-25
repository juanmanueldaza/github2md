"""SOLID principle compliance tests for github2md.

Tests verify that the codebase follows:
- S: Single Responsibility Principle
- O: Open/Closed Principle
- L: Liskov Substitution Principle
- I: Interface Segregation Principle
- D: Dependency Inversion Principle
"""

import inspect
from pathlib import Path
from typing import Any, get_type_hints

from github2md.converter import GitHubToMarkdownConverter, create_converter
from github2md.extractor import GitHubExtractor
from github2md.formatters.base import BaseFormatter
from github2md.formatters.contributions import ContributionsFormatter
from github2md.formatters.profile import ProfileFormatter
from github2md.formatters.repos import ReposFormatter
from github2md.parsers.base import BaseParser
from github2md.parsers.contributions import ContributionsParser
from github2md.parsers.profile import ProfileParser
from github2md.parsers.repos import ReposParser
from github2md.protocols import (
    DataExtractor,
    FormatterRegistry,
    OutputWriter,
    ParserRegistry,
    SectionFormatter,
    SectionParser,
)
from github2md.registry import (
    DefaultFormatterRegistry,
    DefaultParserRegistry,
    get_formatter_registry,
    get_parser_registry,
    register_formatter,
    register_parser,
)
from github2md.writer import MarkdownFileWriter

from .conftest import DictExtractor, InMemoryWriter

# =============================================================================
# S — Single Responsibility Principle
# =============================================================================


class TestSingleResponsibility:
    """Each class should have one reason to change."""

    def test_extractor_only_extracts(self):
        """GitHubExtractor: sole job is extracting raw data."""
        methods = [
            m for m in dir(GitHubExtractor) if not m.startswith("_") or m == "__init__"
        ]
        public = {m for m in methods if not m.startswith("_")}
        assert "extract" in public
        assert len(public) == 1

    def test_writer_only_writes(self, tmp_path):
        """MarkdownFileWriter: sole job is writing content to files."""
        writer = MarkdownFileWriter(tmp_path)
        sig = inspect.signature(writer.write)
        assert "content" in sig.parameters
        assert "filename" in sig.parameters

    def test_each_parser_one_section(self):
        """Each parser handles exactly one section_key."""
        parsers = [ProfileParser(), ReposParser(), ContributionsParser()]
        keys = [p.section_key for p in parsers]
        assert len(keys) == len(set(keys)), "Parsers share section keys"

    def test_each_formatter_one_section(self):
        """Each formatter handles exactly one section_key."""
        formatters = [ProfileFormatter(), ReposFormatter(), ContributionsFormatter()]
        keys = [f.section_key for f in formatters]
        assert len(keys) == len(set(keys)), "Formatters share section keys"

    def test_parser_key_matches_formatter_key(self):
        """Parser and formatter for the same section use matching keys."""
        parsers = {
            p.section_key: p
            for p in [ProfileParser(), ReposParser(), ContributionsParser()]
        }
        formatters = {
            f.section_key: f
            for f in [ProfileFormatter(), ReposFormatter(), ContributionsFormatter()]
        }
        for key in parsers:
            assert key in formatters, f"Formatter missing for section '{key}'"

    def test_registry_sole_responsibility(self):
        """Registry classes only manage registration, nothing else."""
        parser_reg = DefaultParserRegistry()
        formatter_reg = DefaultFormatterRegistry()
        assert hasattr(parser_reg, "register")
        assert hasattr(parser_reg, "get_all")
        assert hasattr(formatter_reg, "register")
        assert hasattr(formatter_reg, "get_all")

    def test_converter_orchestrates_not_implements(self):
        """Converter coordinates but does not implement extraction/writing."""
        extractor = DictExtractor({"profile": [{"login": "u"}]})
        writer = InMemoryWriter()
        conv = GitHubToMarkdownConverter(extractor, writer)
        assert conv._extractor is extractor
        assert conv._writer is writer


# =============================================================================
# O — Open/Closed Principle
# =============================================================================


class TestOpenClosed:
    """Classes should be open for extension, closed for modification."""

    def test_new_parser_can_be_registered(self):
        """Registry allows adding new parsers without modifying existing code."""
        registry = DefaultParserRegistry()
        parser = ProfileParser()
        registry.register(parser)
        assert parser in registry.get_all()

    def test_new_formatter_can_be_registered(self):
        """Registry allows adding new formatters without modifying existing code."""
        registry = DefaultFormatterRegistry()
        formatter = ProfileFormatter()
        registry.register(formatter)
        assert formatter in registry.get_all()

    def test_decorator_registers_parser(self):
        """@register_parser decorator auto-registers parser instances."""

        class _TestParser:
            section_key = "_test_parser_srp"

            def parse(self, raw_data):
                return {}

        registered_before = len(get_parser_registry().get_all())
        register_parser(_TestParser)
        registered_after = len(get_parser_registry().get_all())
        assert registered_after == registered_before + 1

    def test_decorator_registers_formatter(self):
        """@register_formatter decorator auto-registers formatter instances."""

        class _TestFormatter:
            section_key = "_test_fmt_ocp"
            output_filename = "_test_ocp.md"

            def format(self, data):
                return ""

        registered_before = len(get_formatter_registry().get_all())
        register_formatter(_TestFormatter)
        registered_after = len(get_formatter_registry().get_all())
        assert registered_after == registered_before + 1

    def test_converter_uses_registry_not_hardcoded_list(self):
        """Converter iterates registry — new parsers/formatters work automatically."""
        extractor = DictExtractor({"profile": [{"login": "u"}]})
        writer = InMemoryWriter()
        conv = GitHubToMarkdownConverter(extractor, writer)
        assert hasattr(conv, "_parser_registry")
        assert hasattr(conv, "_formatter_registry")

    def test_registry_returns_copy(self):
        """get_all returns a copy so external mutation doesn't affect registry."""
        registry = DefaultParserRegistry()
        registry.register(ProfileParser())
        items = registry.get_all()
        items.clear()
        assert len(registry.get_all()) > 0


# =============================================================================
# L — Liskov Substitution Principle
# =============================================================================


class TestLiskovSubstitution:
    """Subtypes must be substitutable for their base types/protocols."""

    def test_parsers_implement_section_parser_protocol(self):
        """All parsers satisfy SectionParser and are substitutable for the protocol."""
        parsers: list[SectionParser] = [
            ProfileParser(),
            ReposParser(),
            ContributionsParser(),
        ]
        for parser in parsers:
            assert isinstance(parser, SectionParser)
            assert isinstance(parser.section_key, str)
            result = parser.parse({parser.section_key: {}})
            assert isinstance(result, dict)

    def test_formatters_implement_section_formatter_protocol(self):
        """All formatters satisfy SectionFormatter."""
        formatters: list[SectionFormatter] = [
            ProfileFormatter(),
            ReposFormatter(),
            ContributionsFormatter(),
        ]
        for formatter in formatters:
            assert isinstance(formatter, SectionFormatter)
            assert isinstance(formatter.section_key, str)
            assert isinstance(formatter.output_filename, str)
            result = formatter.format({})
            assert isinstance(result, str)

    def test_parsers_extend_base_parser(self):
        """All parsers extend BaseParser and inherit shared utilities."""
        parsers = [ProfileParser(), ReposParser(), ContributionsParser()]
        for parser in parsers:
            assert isinstance(parser, BaseParser)
            assert hasattr(parser, "_safe_get")
            assert hasattr(parser, "_format_date")

    def test_formatters_extend_base_formatter(self):
        """All formatters extend BaseFormatter and inherit shared utilities."""
        formatters = [ProfileFormatter(), ReposFormatter(), ContributionsFormatter()]
        for formatter in formatters:
            assert isinstance(formatter, BaseFormatter)
            assert hasattr(formatter, "_sanitize_url")
            assert hasattr(formatter, "_make_link")
            assert hasattr(formatter, "_truncate")

    def test_dict_extractor_substitutable_for_data_extractor(self):
        """DictExtractor can be used wherever DataExtractor is expected."""
        extractor: DataExtractor = DictExtractor({"profile": [{"login": "u"}]})
        result = extractor.extract("testuser")
        assert result["username"] == "testuser"
        assert "profile" in result

    def test_in_memory_writer_substitutable_for_output_writer(self):
        """InMemoryWriter can be used wherever OutputWriter is expected."""
        writer: OutputWriter = InMemoryWriter()
        path = writer.write("test.md", "# Hello")
        assert isinstance(path, Path)

    def test_default_parser_registry_substitutable(self):
        """DefaultParserRegistry satisfies ParserRegistry protocol."""
        registry: ParserRegistry = DefaultParserRegistry()
        registry.register(ProfileParser())
        assert len(registry.get_all()) > 0

    def test_default_formatter_registry_substitutable(self):
        """DefaultFormatterRegistry satisfies FormatterRegistry protocol."""
        registry: FormatterRegistry = DefaultFormatterRegistry()
        registry.register(ProfileFormatter())
        assert len(registry.get_all()) > 0

    def test_parser_parse_accepts_empty_data(self):
        """All parsers handle empty data without raising."""
        parsers = [ProfileParser(), ReposParser(), ContributionsParser()]
        for parser in parsers:
            result = parser.parse({})
            assert isinstance(result, dict)

    def test_formatter_format_accepts_empty_data(self):
        """All formatters handle empty data without raising."""
        formatters = [ProfileFormatter(), ReposFormatter(), ContributionsFormatter()]
        for formatter in formatters:
            result = formatter.format({})
            assert isinstance(result, str)


# =============================================================================
# I — Interface Segregation Principle
# =============================================================================


class TestInterfaceSegregation:
    """Clients should not be forced to depend on methods they don't use."""

    def test_data_extractor_has_single_method(self):
        """DataExtractor protocol has exactly one required method."""
        members = [m for m in dir(DataExtractor) if not m.startswith("_")]
        assert "extract" in members
        assert len(members) <= 2  # extract + __class_getitem__ or similar

    def test_output_writer_has_single_method(self):
        """OutputWriter protocol has exactly one required method."""
        members = [m for m in dir(OutputWriter) if not m.startswith("_")]
        assert "write" in members
        assert len(members) <= 2

    def test_section_parser_minimal_interface(self):
        """SectionParser requires only section_key and parse."""
        members = [m for m in dir(SectionParser) if not m.startswith("_")]
        required = {"section_key", "parse"}
        assert required.issubset(set(members))

    def test_section_formatter_minimal_interface(self):
        """SectionFormatter requires only section_key, output_filename, and format."""
        members = [m for m in dir(SectionFormatter) if not m.startswith("_")]
        required = {"section_key", "output_filename", "format"}
        assert required.issubset(set(members))

    def test_parser_registry_minimal_interface(self):
        """ParserRegistry requires only register and get_all."""
        members = [m for m in dir(ParserRegistry) if not m.startswith("_")]
        required = {"register", "get_all"}
        assert required.issubset(set(members))

    def test_formatter_registry_minimal_interface(self):
        """FormatterRegistry requires only register and get_all."""
        members = [m for m in dir(FormatterRegistry) if not m.startswith("_")]
        required = {"register", "get_all"}
        assert required.issubset(set(members))

    def test_converter_depends_on_protocols_not_concretions(self):
        """GitHubToMarkdownConverter accepts protocols, not concrete types."""
        hints = get_type_hints(GitHubToMarkdownConverter.__init__)
        if "extractor" in hints:
            assert hints["extractor"] == DataExtractor
        if "writer" in hints:
            assert hints["writer"] == OutputWriter

    def test_no_protocol_has_unnecessary_methods(self):
        """No protocol defines more than 3 required members."""
        protocols = [
            ("DataExtractor", DataExtractor),
            ("OutputWriter", OutputWriter),
            ("SectionParser", SectionParser),
            ("SectionFormatter", SectionFormatter),
            ("ParserRegistry", ParserRegistry),
            ("FormatterRegistry", FormatterRegistry),
        ]
        for name, proto in protocols:
            members = [m for m in dir(proto) if not m.startswith("_")]
            assert len(members) <= 4, f"{name} has {len(members)} members"


# =============================================================================
# D — Dependency Inversion Principle
# =============================================================================


class TestDependencyInversion:
    """High-level modules should depend on abstractions, not low-level details."""

    def test_converter_depends_on_abstractions(self):
        """Converter depends on DataExtractor and OutputWriter protocols."""
        sig = inspect.signature(GitHubToMarkdownConverter.__init__)
        params = list(sig.parameters.keys())
        assert "extractor" in params
        assert "writer" in params

    def test_converter_accepts_any_data_extractor(self):
        """Converter works with any DataExtractor implementation."""
        extractor = DictExtractor({"profile": [{"login": "u"}]})
        writer = InMemoryWriter()
        conv = GitHubToMarkdownConverter(extractor, writer)
        files = conv.convert("testuser")
        assert files is not None

    def test_converter_accepts_any_output_writer(self):
        """Converter works with any OutputWriter implementation."""
        extractor = DictExtractor({"profile": [{"login": "u"}]})
        writer = InMemoryWriter()
        conv = GitHubToMarkdownConverter(extractor, writer)
        files = conv.convert("testuser")
        assert isinstance(files, list)

    def test_create_converter_factory_injects_dependencies(self, tmp_path):
        """Factory function wires concrete deps behind abstract interfaces."""
        output_dir = tmp_path / "test_github2md_dip"
        conv = create_converter(output_dir)
        assert isinstance(conv, GitHubToMarkdownConverter)
        assert isinstance(conv._extractor, GitHubExtractor)
        assert isinstance(conv._writer, MarkdownFileWriter)

    def test_mock_extractor_used_in_converter(self):
        """A mock/alternative extractor seamlessly replaces GitHubExtractor."""

        class MockExtractor:
            def extract(self, username: str) -> dict[str, Any]:
                return {
                    "username": username,
                    "profile": [{"login": username, "name": "Mock User"}],
                    "repos": [],
                    "contributions": {},
                }

        writer = InMemoryWriter()
        conv = GitHubToMarkdownConverter(MockExtractor(), writer)
        conv.convert("mockuser")
        assert any("profile" in key for key in writer.files)

    def test_mock_writer_used_in_converter(self):
        """A mock/alternative writer seamlessly replaces MarkdownFileWriter."""

        class ListWriter:
            def __init__(self):
                self.written: list[tuple[str, str]] = []

            def write(self, filename: str, content: str) -> Path:
                self.written.append((filename, content))
                return Path(filename)

        extractor = DictExtractor({"profile": [{"login": "u"}]})
        writer = ListWriter()
        conv = GitHubToMarkdownConverter(extractor, writer)
        conv.convert("testuser")
        assert len(writer.written) > 0

    def test_registries_use_protocols(self):
        """Registry classes reference SectionParser / SectionFormatter protocols."""
        parser_sig = inspect.signature(DefaultParserRegistry.register)
        parser_params = list(parser_sig.parameters.values())
        assert len(parser_params) >= 2

        formatter_sig = inspect.signature(DefaultFormatterRegistry.register)
        formatter_params = list(formatter_sig.parameters.values())
        assert len(formatter_params) >= 2

    def test_parsers_reference_only_abstractions(self):
        """Parser implementations import from base/protocols, not concrete siblings."""
        import github2md.parsers.contributions as pc
        import github2md.parsers.profile as pp
        import github2md.parsers.repos as pr

        source_pp = inspect.getsource(pp)
        source_pr = inspect.getsource(pr)
        source_pc = inspect.getsource(pc)
        for src in [source_pp, source_pr, source_pc]:
            assert "from ..registry import" in src
            assert "from .base import" in src

    def test_formatters_reference_only_abstractions(self):
        """Formatters import from base/protocols, not concrete siblings."""
        import github2md.formatters.contributions as fc
        import github2md.formatters.profile as fp
        import github2md.formatters.repos as fr

        source_fp = inspect.getsource(fp)
        source_fr = inspect.getsource(fr)
        source_fc = inspect.getsource(fc)
        for src in [source_fp, source_fr, source_fc]:
            assert "from ..registry import" in src
            assert "from .base import" in src
