"""Tests for the command-line interface."""

import argparse
from unittest.mock import MagicMock, patch
import pytest
from soap_calc import cli
from soap_calc.models import Recipe, OilEntry, LyeResult, RecipeResult
from soap_calc.oils import OLIVE_OIL

@pytest.fixture
def mock_recipe():
    return Recipe(
        name="Test Recipe",
        oils=[OilEntry(oil=OLIVE_OIL, percentage=100.0)],
        default_oil_weight=500.0,
    )

@pytest.fixture
def mock_result():
    return RecipeResult(
        lye=LyeResult(naoh_amount=50.0),
        total_liquid=100.0,
        liquid_breakdown=[],
        total_oil_weight=500.0,
        total_batch_weight=650.0,
        fatty_acid_profile=MagicMock(),
        properties=MagicMock(),
    )

class TestCliCommands:
    @patch("soap_calc.cli.load_recipe")
    @patch("soap_calc.cli.calculate")
    @patch("soap_calc.cli.render_markdown")
    def test_cmd_calculate(self, mock_render, mock_calc, mock_load, mock_recipe, mock_result):
        mock_load.return_value = mock_recipe
        mock_calc.return_value = mock_result
        mock_render.return_value = "Markdown Output"

        args = argparse.Namespace(recipe="recipe.json", oil_weight=None)
        cli._cmd_calculate(args)

        mock_load.assert_called_with("recipe.json")
        mock_calc.assert_called_with(mock_recipe, oil_weight=None)
        # We can't easily capture print output with simple unittests without capsys/capsysbinary fixture usually, 
        # but the function execution is what matters here.

    @patch("soap_calc.cli.load_recipe")
    @patch("soap_calc.cli.calculate")
    @patch("soap_calc.cli.render_markdown")
    def test_cmd_calculate_override(self, mock_render, mock_calc, mock_load, mock_recipe, mock_result):
        mock_load.return_value = mock_recipe
        mock_calc.return_value = mock_result
        
        args = argparse.Namespace(recipe="recipe.json", oil_weight=1000.0)
        cli._cmd_calculate(args)

        mock_calc.assert_called_with(mock_recipe, oil_weight=1000.0)

    @patch("soap_calc.cli.load_recipe")
    @patch("soap_calc.cli.calculate")
    @patch("soap_calc.cli.export_markdown")
    def test_cmd_export(self, mock_export, mock_calc, mock_load, mock_recipe, mock_result):
        mock_load.return_value = mock_recipe
        mock_calc.return_value = mock_result
        
        # Test implicit output path
        args = argparse.Namespace(recipe="recipe.json", output=None, oil_weight=None)
        with patch("sys.stdout"): # Suppress print
            cli._cmd_export(args)
        
        mock_export.assert_called()
        call_args = mock_export.call_args
        assert str(call_args[0][2]) == "recipe.md"

        # Test explicit output path
        args = argparse.Namespace(recipe="recipe.json", output="out.md", oil_weight=None)
        with patch("sys.stdout"):
            cli._cmd_export(args)
        
        call_args = mock_export.call_args
        assert call_args[0][2] == "out.md"

    @patch("soap_calc.cli.load_recipe")
    @patch("soap_calc.cli.validate")
    def test_cmd_validate_clean(self, mock_validate, mock_load, mock_recipe):
        mock_load.return_value = mock_recipe
        mock_validate.return_value = [] # No warnings

        args = argparse.Namespace(recipe="recipe.json")
        with patch("sys.stdout"):
            cli._cmd_validate(args)
        # Should not exit
    
    @patch("soap_calc.cli.load_recipe")
    @patch("soap_calc.cli.validate")
    def test_cmd_validate_warnings(self, mock_validate, mock_load, mock_recipe):
        mock_load.return_value = mock_recipe
        mock_validate.return_value = ["Warning 1"]

        args = argparse.Namespace(recipe="recipe.json")
        with patch("sys.stdout"), pytest.raises(SystemExit) as e:
            cli._cmd_validate(args)
        assert e.value.code == 1

    @patch("soap_calc.cli.list_oils")
    @patch("soap_calc.cli.search_oils")
    def test_cmd_list_oils(self, mock_search, mock_list):
        mock_list.return_value = [OLIVE_OIL]
        
        # No query
        args = argparse.Namespace(query=None)
        with patch("sys.stdout"):
            cli._cmd_list_oils(args)
        mock_list.assert_called()
        mock_search.assert_not_called()

        # With query
        args = argparse.Namespace(query="olive")
        mock_search.return_value = [OLIVE_OIL]
        with patch("sys.stdout"):
            cli._cmd_list_oils(args)
        mock_search.assert_called_with("olive")

    @patch("soap_calc.cli.load_recipe")
    @patch("soap_calc.cli.scale_recipe")
    @patch("soap_calc.cli.save_recipe")
    @patch("soap_calc.cli.calculate")
    @patch("soap_calc.cli.render_markdown")
    def test_cmd_scale(self, mock_render, mock_calc, mock_save, mock_scale, mock_load, mock_recipe, mock_result):
        mock_load.return_value = mock_recipe
        mock_scale.return_value = mock_recipe # Return same for simplicity
        mock_calc.return_value = mock_result

        # Save to file
        args = argparse.Namespace(recipe="r.json", target_oil=100.0, output="out.json")
        with patch("sys.stdout"):
            cli._cmd_scale(args)
        mock_scale.assert_called_with(mock_recipe, 100.0)
        mock_save.assert_called_with(mock_recipe, "out.json")

        # Print to stdout
        args = argparse.Namespace(recipe="r.json", target_oil=100.0, output=None)
        with patch("sys.stdout"):
            cli._cmd_scale(args)
        mock_calc.assert_called_with(mock_recipe)
        mock_render.assert_called()

class TestCliParser:
    def test_parser_creation(self):
        parser = cli.build_parser()
        assert parser is not None
        
        # Test parsing a simple command
        args = parser.parse_args(["calculate", "recipe.json"])
        assert args.command == "calculate"
        assert args.recipe == "recipe.json"

    def test_parser_scale(self):
        parser = cli.build_parser()
        args = parser.parse_args(["scale", "recipe.json", "500"])
        assert args.command == "scale"
        assert args.target_oil == 500.0

