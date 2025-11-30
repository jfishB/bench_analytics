from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from lineups.models import Lineup, LineupPlayer
from roster.models import Player, Team


class LineupAPITests(TestCase):
    """High-level Django tests for the lineup app.
    Covers:
    - Manual lineup save with explicit players + batting orders
    - Missing batting orders rejection
    - Duplicate batting orders rejection
    - Detail retrieval for a single lineup
    - Delete permissions (creator vs. other vs. superuser)
    """

    def setUp(self):
        self.client = APIClient()
        self.base_url = "/api/v1/lineups/"

        # Create team and 9 players with minimal stats for algorithm
        self.team = Team.objects.create()
        self.players = []
        for i in range(9):
            p = Player.objects.create(
                name=f"Player {i+1}",
                team=self.team,
                # minimal stats to keep simulator/algorithm happy
                b_game=10.0,
                pa=40 + i,
                hit=10 + i,
                home_run=1 + (i % 3),
                walk=2 + (i % 2),
            )
            self.players.append(p)

        User = get_user_model()
        self.creator = User.objects.create_user(username="creator",
                                                password="pw")
        self.other = User.objects.create_user(username="other",
                                              password="pw")
        self.superuser = User.objects.create_superuser(username="admin",
                                                       password="pw")

    def test_manual_save_creates_persisted_lineup(self):
        """POST with players + batting orders should persist
        a Lineup and players."""
        payload = {
            "team_id": self.team.id,
            "name": "Manual Lineup",
            "players": [
                {"player_id": p.id, "batting_order": idx + 1}
                for idx, p in enumerate(self.players)
            ],
        }

        self.client.force_authenticate(user=self.creator)
        resp = self.client.post(self.base_url, payload, format="json")
        self.assertEqual(resp.status_code, 201)

        data = resp.json()
        self.assertIn("id", data)
        lineup_id = data["id"]

        lineup = Lineup.objects.filter(pk=lineup_id).first()
        self.assertIsNotNone(lineup)
        self.assertEqual(lineup.team_id, self.team.id)
        self.assertEqual(lineup.name, "Manual Lineup")
        self.assertEqual(lineup.created_by_id, self.creator.id)

        lp_qs = LineupPlayer.objects.filter(lineup=lineup)\
            .order_by("batting_order")
        self.assertEqual(lp_qs.count(), 9)
        for idx, lp in enumerate(lp_qs):
            self.assertEqual(lp.batting_order, idx + 1)
            self.assertEqual(lp.player.team_id, self.team.id)

    def test_rejects_missing_batting_orders(self):
        """Payload without batting_order is treated as team_id-only and
          generates a suggestion."""
        payload = {
            "team_id": self.team.id,
            "players": [
                {"player_id": p.id}  # missing batting_order
                for p in self.players
            ],
        }

        self.client.force_authenticate(user=self.creator)
        resp = self.client.post(self.base_url, payload, format="json")
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertIn("players", data)
        # Only a suggested lineup is generated, nothing is saved
        self.assertEqual(Lineup.objects.count(), 0)

    def test_team_id_only_generates_suggested_lineup(self):
        """POST with only team_id and player_ids generates a
        suggested lineup without saving it."""
        # Use the 9 players already created in setUp
        player_ids = [p.id for p in self.players]
        payload = {
            "team_id": self.team.id,
            "players": [{"player_id": pid} for pid in player_ids]
        }

        self.client.force_authenticate(user=self.creator)
        resp = self.client.post(self.base_url, payload, format="json")
        self.assertEqual(resp.status_code, 201)

        data = resp.json()
        self.assertEqual(data["team_id"], self.team.id)
        self.assertIn("players", data)
        self.assertEqual(len(data["players"]), 9)
        self.assertEqual(Lineup.objects.count(), 0)

    def test_detail_endpoint_returns_lineup(self):
        """GET /lineups/saved/<id>/ returns a single lineup via ViewSet."""
        lineup = Lineup.objects.create(team=self.team, created_by=self.creator)
        LineupPlayer.objects.create(
            lineup=lineup,
            player=self.players[0],
            batting_order=1,
        )

        # ViewSet is mounted at /saved/ so URL is /api/v1/lineups/saved/<id>/
        url = f"{self.base_url}saved/{lineup.id}/"
        self.client.force_authenticate(user=self.creator)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["id"], lineup.id)

    def test_delete_permissions_creator_other_superuser(self):
        """Only creator or superuser may delete a lineup."""
        lineup = Lineup.objects.create(team=self.team, created_by=self.creator)
        url = f"{self.base_url}{lineup.id}/"

        # unauthenticated -> 401 (IsAuthenticated permission)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 401)

        # other user -> 403 (authenticated but not authorized)
        self.client.force_authenticate(user=self.other)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 403)

        # creator -> 204
        self.client.force_authenticate(user=self.creator)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)

        # recreate and ensure superuser can delete
        lineup = Lineup.objects.create(team=self.team, created_by=self.creator)
        url = f"{self.base_url}{lineup.id}/"
        self.client.force_authenticate(user=self.superuser)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 204)


class LineupModelTests(TestCase):
    """Tests for Lineup and LineupPlayer models.
    Covers basic creation and __str__ methods."""
    def setUp(self):
        self.team = Team.objects.create()
        self.player = Player.objects.create(name="Player 1", team=self.team)
        User = get_user_model()
        self.creator = User.objects.create_user(username="creator_model",
                                                password="pw")

    def test_create_lineup_and_player(self):
        lineup = Lineup.objects.create(team=self.team, created_by=self.creator)
        lp = LineupPlayer.objects.create(lineup=lineup, player=self.player,
                                         batting_order=1)
        self.assertEqual(lp.lineup, lineup)
        self.assertEqual(lp.player, self.player)
        self.assertEqual(lp.batting_order, 1)

        self.assertEqual(lineup.players.count(), 1)

    def test_model_str_methods(self):
        """Test __str__ methods for Lineup and LineupPlayer models."""
        # Test Lineup __str__
        lineup = Lineup.objects.create(
            team=self.team,
            name="Test Lineup",
            created_by=self.creator
        )
        str_repr = str(lineup)
        self.assertIn("Test Lineup", str_repr)
        self.assertIn(f"Team {self.team.id}", str_repr)
        # Test LineupPlayer __str__
        lp = LineupPlayer.objects.create(
            lineup=lineup,
            player=self.player,
            batting_order=3
        )
        str_repr = str(lp)
        self.assertIn("3.", str_repr)
        self.assertIn("Player 1", str_repr)


class LineupValidationTests(TestCase):
    """Tests for lineup validation logic to achieve 100% coverage.
    Covers edge cases in validator.py not hit by other tests."""

    def setUp(self):
        self.team = Team.objects.create()
        self.players = []
        for i in range(9):
            p = Player.objects.create(
                name=f"Player {i+1}",
                team=self.team,
                b_game=10.0,
                pa=40 + i,
                hit=10 + i,
                home_run=1 + (i % 3),
                walk=2 + (i % 2),
            )
            self.players.append(p)

        User = get_user_model()
        self.creator = User.objects.create_user(username="creator",
                                                password="pw")

    def test_api_validation_batting_order_errors(self):
        """Test API validation for batting order related errors."""
        client = APIClient()
        client.force_authenticate(user=self.creator)
        # Test duplicate batting orders
        payload = {
            "team_id": self.team.id,
            "name": "Duplicate Orders",
            "players": [
                {"player_id": self.players[0].id, "batting_order": 1},
                # duplicate
                {"player_id": self.players[1].id, "batting_order": 1},
            ] + [{"player_id": p.id, "batting_order": i+3} for i,
                 p in enumerate(self.players[2:])],
        }
        resp = client.post("/api/v1/lineups/", payload, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Batting orders must be unique", str(resp.data))
        # Test invalid batting order range
        payload = {
            "team_id": self.team.id,
            "name": "Invalid Range",
            "players": [{"player_id": p.id, "batting_order": i+2} for i,
                        p in enumerate(self.players)],
        }
        resp = client.post("/api/v1/lineups/", payload, format="json")
        self.assertEqual(resp.status_code, 400)
        # Test wrong number of players
        payload = {
            "team_id": self.team.id,
            "name": "Too Few Players",
            "players": [{"player_id": p.id, "batting_order": i+1} for i,
                        p in enumerate(self.players[:2])],
        }
        resp = client.post("/api/v1/lineups/", payload, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Exactly 9 players", str(resp.data))

    def test_api_validation_data_errors(self):
        """Test API validation for team and player data errors."""
        client = APIClient()
        client.force_authenticate(user=self.creator)
        # Test nonexistent team
        payload = {
            "team_id": 99999,
            "name": "Bad Team",
            "players": [{"player_id": p.id, "batting_order": i+1}
                        for i, p in enumerate(self.players)],
        }
        resp = client.post("/api/v1/lineups/", payload, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Unknown team", str(resp.data))
        # Test nonexistent player
        payload = {
            "team_id": self.team.id,
            "name": "Bad Players",
            "players": [{"player_id": 99999, "batting_order": 1}] +
                       [{"player_id": p.id, "batting_order": i+2}
                        for i, p in enumerate(self.players[1:])],
        }
        resp = client.post("/api/v1/lineups/", payload, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Players not found", str(resp.data))
        # Test players from wrong team
        other_team = Team.objects.create()
        wrong_player = Player.objects.create(
            name="Wrong Team Player", team=other_team,
            b_game=10.0, pa=40, hit=10, home_run=1, walk=2,
        )
        payload = {
            "team_id": self.team.id,
            "name": "Mixed Teams",
            "players": [{"player_id": wrong_player.id, "batting_order": 1}] +
                    [{"player_id": p.id, "batting_order": i+2} for i,
                        p in enumerate(self.players[1:])],
        }
        resp = client.post("/api/v1/lineups/", payload, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Players must belong to the same team", str(resp.data))

    def test_unauthenticated_manual_save_rejected(self):
        """Manual save without authentication should be rejected."""
        client = APIClient()
        # Don't authenticate
        payload = {
            "team_id": self.team.id,
            "name": "Unauthenticated Lineup",
            "players": [
                {"player_id": p.id, "batting_order": idx + 1}
                for idx, p in enumerate(self.players)
            ],
        }

        resp = client.post("/api/v1/lineups/", payload, format="json")
        self.assertEqual(resp.status_code, 403)
        self.assertIn("Authentication required", str(resp.data))

    def test_get_helper_function_all_paths(self):
        """Test _get helper function with all possible input
        types and edge cases."""
        from lineups.services.validator import _get
        from lineups.services.input_data import LineupPlayerInput
        # Test with None object returns default
        result = _get(None, "any_key", "default_value")
        self.assertEqual(result, "default_value")
        # Test with None object and no default returns None
        result = _get(None, "any_key")
        self.assertIsNone(result)
        # Test with unknown type (string - neither hasattr success nor dict)
        result = _get("some_string", "attr", "default")
        self.assertEqual(result, "default")
        # Test with dataclass object (hasattr path)
        player_input = LineupPlayerInput(player_id=1, batting_order=1)
        result = _get(player_input, "player_id")
        self.assertEqual(result, 1)
        # Test with dict (isinstance dict path)
        dict_obj = {"player_id": 2}
        result = _get(dict_obj, "player_id")
        self.assertEqual(result, 2)

        # Test with object without attribute
        class ObjWithoutAttr:
            pass
        obj = ObjWithoutAttr()
        result = _get(obj, "nonexistent_attr", "my_default")
        self.assertEqual(result, "my_default")

    def test_validate_batting_orders_with_neither_dataclass_nor_dict(self):
        """Test validator.py line 32: validate_batting_orders with object
        that's neither dataclass nor dict."""
        from lineups.services.validator import validate_batting_orders
        from lineups.services.exceptions import BadBattingOrder

        # Create a simple object that's neither dataclass nor dict
        class SimpleObject:
            pass
        players = [SimpleObject() for _ in range(9)]
        # Should raise BadBattingOrder because bo will be None
        # (line 32 else branch)
        with self.assertRaises(BadBattingOrder) as cm:
            validate_batting_orders(players)
        self.assertIn("All players must have a batting order",
                      str(cm.exception))


class LineupViewSetTests(TestCase):
    """Tests for LineupViewSet to cover remaining view logic.
    Covers queryset filtering by user and permissions."""

    def setUp(self):
        self.team = Team.objects.create()
        self.player = Player.objects.create(
            name="Player 1",
            team=self.team,
            b_game=10.0,
            pa=40,
            hit=10,
            home_run=1,
            walk=2,
        )

        User = get_user_model()
        self.creator = User.objects.create_user(username="creator",
                                                password="pw")
        self.superuser = User.objects.create_superuser(username="admin",
                                                       password="pw")
        self.other = User.objects.create_user(username="other", password="pw")

    def test_viewset_queryset_unauthenticated_scenarios(self):
        """Test all unauthenticated user scenarios return empty
        queryset or 401."""
        from lineups.views import LineupViewSet
        from unittest.mock import Mock
        # Test 1: Unauthenticated API request gets 401
        client = APIClient()
        resp = client.get("/api/v1/lineups/saved/")
        self.assertEqual(resp.status_code, 401)
        # Test 2: ViewSet with None user
        viewset = LineupViewSet()
        mock_request = Mock()
        mock_request.user = None
        viewset.request = mock_request
        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 0)
        # Test 3: ViewSet with unauthenticated user object
        viewset = LineupViewSet()
        mock_request = Mock()
        mock_user = Mock()
        mock_user.is_authenticated = False
        mock_request.user = mock_user
        viewset.request = mock_request
        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 0)

    def test_viewset_queryset_for_superuser(self):
        """Superuser should see all lineups."""
        Lineup.objects.create(team=self.team, created_by=self.creator,
                              name="Lineup 1")
        Lineup.objects.create(team=self.team, created_by=self.other,
                              name="Lineup 2")

        client = APIClient()
        client.force_authenticate(user=self.superuser)
        resp = client.get("/api/v1/lineups/saved/")
        self.assertEqual(resp.status_code, 200)
        # Superuser sees both lineups
        self.assertEqual(len(resp.data), 2)

    def test_viewset_queryset_filters_by_user(self):
        """Normal users should only see their own lineups."""
        Lineup.objects.create(team=self.team, created_by=self.creator,
                              name="My Lineup")
        Lineup.objects.create(team=self.team, created_by=self.other,
                              name="Other Lineup")

        client = APIClient()
        client.force_authenticate(user=self.creator)
        resp = client.get("/api/v1/lineups/saved/")
        self.assertEqual(resp.status_code, 200)
        # Creator only sees their own lineup
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["name"], "My Lineup")


class LineupServiceTests(TestCase):
    """Unit tests for lineup services to achieve 100% coverage.
    Covers edge cases in service functions not hit by other tests."""

    def setUp(self):
        self.team = Team.objects.create()
        self.players = []
        for i in range(9):
            p = Player.objects.create(
                name=f"Player {i+1}",
                team=self.team,
                b_game=10.0,
                pa=40 + i,
                hit=10 + i,
                home_run=1 + (i % 3),
                walk=2 + (i % 2),
            )
            self.players.append(p)

        User = get_user_model()
        self.creator = User.objects.create_user(username="creator",
                                                password="pw")

    def test_validate_batting_orders_comprehensive(self):
        """Test validate_batting_orders with different inputs
        and error cases."""
        from lineups.services.validator import validate_batting_orders
        from lineups.services.input_data import LineupPlayerInput
        from lineups.services.exceptions import BadBattingOrder
        # Test with dicts (valid)
        players_dict = \
            [{"player_id": p.id, "batting_order": idx + 1} for idx,
             p in enumerate(self.players)]
        validate_batting_orders(players_dict)
        # Test with dataclass objects (valid)
        players_dataclass = \
            [LineupPlayerInput(player_id=p.id, batting_order=idx + 1)
             for idx, p in enumerate(self.players)]
        validate_batting_orders(players_dataclass)
        # Test None batting_order rejection
        players_none = [{"player_id": p.id, "batting_order": None}
                        for p in self.players]
        with self.assertRaises(BadBattingOrder) as cm:
            validate_batting_orders(players_none)
        self.assertIn("must have a batting order", str(cm.exception))
        # Test wrong player count rejection
        players_few = [{"player_id": p.id, "batting_order": idx + 1} for idx,
                       p in enumerate(self.players[:5])]
        with self.assertRaises(BadBattingOrder) as cm:
            validate_batting_orders(players_few)
        self.assertIn("exactly 9 players", str(cm.exception))

    def test_validate_lineup_model_batting_order_errors(self):
        """Test validate_lineup_model rejects invalid batting orders."""
        from lineups.services.validator import validate_lineup_model
        from lineups.services.exceptions import BadBattingOrder
        # Test missing batting_order (None)
        lineup1 = Lineup.objects.create(team=self.team,
                                        created_by=self.creator)
        LineupPlayer.objects.create(lineup=lineup1, player=self.players[0],
                                    batting_order=None)
        with self.assertRaises(BadBattingOrder):
            validate_lineup_model(lineup1)
        # Test non-consecutive batting orders
        lineup2 = Lineup.objects.create(team=self.team,
                                        created_by=self.creator)
        for idx, p in enumerate(self.players):
            order = idx + 1 if idx < 1 else idx + 2
            # 1, 3, 4, 5, 6, 7, 8, 9, 10
            LineupPlayer.objects.create(lineup=lineup2, player=p,
                                        batting_order=order)
        with self.assertRaises(BadBattingOrder):
            validate_lineup_model(lineup2)

    def test_validate_data_creator_handling(self):
        """Test validate_data with required and optional creator scenarios."""
        from lineups.services.validator import validate_data
        from lineups.services.databa_access import fetch_lineup_data
        from lineups.services.exceptions import NoCreator
        from django.contrib.auth import get_user_model
        payload_dict = {
            "team_id": self.team.id,
            "players": [{"player_id": p.id} for p in self.players],
            "requested_user_id": None,
        }
        # Test require_creator=True raises NoCreator when no users exist
        User = get_user_model()
        User.objects.all().delete()
        with self.assertRaises(NoCreator):
            validate_data(payload_dict, require_creator=True)
        # Test require_creator=False doesn't raise
        validate_data(payload_dict, require_creator=False)
        result = fetch_lineup_data(payload_dict)
        self.assertIsNone(result["created_by_id"])

    def test_validate_lineup_model_error_cases(self):
        """Test validate_lineup_model with various error conditions."""
        from lineups.services.validator import validate_lineup_model
        from lineups.services.exceptions import (PlayersNotFound,
                                                 PlayersWrongTeam)
        # Test None input
        with self.assertRaises(PlayersNotFound):
            validate_lineup_model(None)
        # Test lineup without team
        lineup_no_team = Lineup(name="Test", created_by=self.creator)
        lineup_no_team.team_id = None
        with self.assertRaises(PlayersWrongTeam):
            validate_lineup_model(lineup_no_team)
        # Test lineup without players
        lineup_empty = Lineup.objects.create(team=self.team,
                                             created_by=self.creator)
        with self.assertRaises(PlayersNotFound):
            validate_lineup_model(lineup_empty)
        # Test lineup with player from wrong team
        other_team = Team.objects.create()
        wrong_player = Player.objects.create(
            name="Wrong Team", team=other_team,
            b_game=10.0, pa=40, hit=10, home_run=1, walk=2,
        )
        lineup_wrong = Lineup.objects.create(team=self.team,
                                             created_by=self.creator)
        LineupPlayer.objects.create(lineup=lineup_wrong, player=wrong_player,
                                    batting_order=1)
        with self.assertRaises(PlayersWrongTeam):
            validate_lineup_model(lineup_wrong)

    def test_validate_data_player_id_formats(self):
        """Test validate_data with different player ID format
          and edge cases."""
        from lineups.services.validator import validate_data
        from lineups.services.databa_access import fetch_lineup_data
        from lineups.services.exceptions import PlayersNotFound
        # Test with plain integers (valid)
        payload_ints = {
            "team_id": self.team.id,
            "players": [p.id for p in self.players],
            "requested_user_id": self.creator.id,
        }
        validate_data(payload_ints)
        result = fetch_lineup_data(payload_ints)
        self.assertEqual(result["team"].id, self.team.id)
        self.assertEqual(len(result["players"]), 9)
        # Test with None player_id (invalid)
        payload_none = {
            "team_id": self.team.id,
            "players": [
                {"player_id": self.players[0].id},
                {"player_id": None},
            ] + [{"player_id": p.id} for p in self.players[2:]],
            "requested_user_id": self.creator.id,
        }
        with self.assertRaises(PlayersNotFound):
            validate_data(payload_none)


class LineupAlgorithmTests(TestCase):
    """Tests for algorithm-specific edge cases."""

    def setUp(self):
        self.team = Team.objects.create()
        User = get_user_model()
        self.creator = User.objects.create_user(username="creator",
                                                password="pw")

    def test_generate_suggested_lineup_empty_roster(self):
        """Test generate_suggested_lineup raises DomainError when no player
          IDs provided."""
        from lineups.interactor import LineupCreationInteractor
        from lineups.services.exceptions import DomainError
        # Team has no players, no player_ids provided
        # (selected_player_ids=None)
        interactor = LineupCreationInteractor()
        with self.assertRaises(DomainError) as cm:
            interactor.generate_suggested_lineup(self.team.id,
                                                 selected_player_ids=None)
        self.assertIn("Player IDs are required", str(cm.exception))

    def test_calculate_player_adjustments_with_invalid_b_game(self):
        """Test calculate_player_adjustments when player has
          b_game=0 or None."""
        from lineups.services.algorithm_logic import (
            calculate_player_adjustments
        )
        adjustments = {
            "h_adj": 0, "hr_adj": 0, "bb_adj": 0, "ibb_adj": 0, "hbp_adj": 0,
            "sb_adj": 0, "cs_adj": 0, "gidp_adj": 0, "sf_adj": 0, "sh_adj": 0,
            "tb_adj": 0
        }
        # Test with b_game=0
        player_zero = Player.objects.create(
            name="Zero Games",
            team=self.team,
            b_game=0,
            pa=0,
            hit=0,
            home_run=0,
            walk=0,
        )
        result = calculate_player_adjustments(player_zero, 1, adjustments)
        self.assertEqual(result, adjustments)

        # Test with b_game=None
        player_none = Player.objects.create(
            name="None Games",
            team=self.team,
            b_game=None,
            pa=10,
            hit=5,
            home_run=1,
            walk=2,
        )
        result = calculate_player_adjustments(player_none, 1, adjustments)
        self.assertEqual(result, adjustments)

    def test_calculate_baserun_with_zero_denominator(self):
        """Test calculate_player_baserun_values returns 0 when
          b+c is 0 (line 143)."""
        from lineups.services.algorithm_logic import (
                        calculate_player_baserun_values
                        )
        # Create players with all zero stats that result in b+c = 0
        players = []
        for i in range(9):
            p = Player.objects.create(
                name=f"Zero Stats Player {i+1}",
                team=self.team,
                b_game=1,  # Must be > 0 to avoid line 47
                pa=0,
                hit=0,
                home_run=0,
                walk=0,
                b_hit_by_pitch=0,
                b_intent_walk=0,
                r_total_stolen_base=0,
                r_total_caught_stealing=0,
                b_gnd_into_dp=0,
                b_sac_fly=0,
                b_sac_bunt=0,
                single=0,
                double=0,
                triple=0,
            )
            players.append(p)
        lineup_tuple = tuple(players)
        result = calculate_player_baserun_values(lineup_tuple)
        self.assertEqual(result, 0)

    def test_algorithm_create_lineup_no_valid_permutations(self):
        """Test algorithm_create_lineup returns empty tuple when no
        lineup found (line 176)."""
        from lineups.services.algorithm_logic import algorithm_create_lineup
        from lineups.services.input_data import (
            CreateLineupInput, LineupPlayerInput
            )
        from unittest.mock import patch
        # Create players with b_game=0 so no valid runs can be calculated
        players = []
        for i in range(9):
            p = Player.objects.create(
                name=f"Zero Game Player {i+1}",
                team=self.team,
                b_game=0,  # Will cause all adjustments to fail
                pa=0,
                hit=0,
                home_run=0,
                walk=0,
            )
            players.append(p)
        payload = CreateLineupInput(
            team_id=self.team.id,
            players=[LineupPlayerInput(player_id=p.id) for p in players],
            requested_user_id=None,
        )
        # Mock permutations to return empty to trigger line 176
        with patch('lineups.services.algorithm_logic.permutations') \
             as mock_perms:
            mock_perms.return_value = []  # No permutations
            result = algorithm_create_lineup(payload)
            self.assertEqual(result, tuple())  # Empty tuple


class LineupCreationHandlerTests(TestCase):
    """Tests for lineup_creation_handler.py edge cases."""

    def setUp(self):
        self.team = Team.objects.create()
        self.players = []
        for i in range(9):
            p = Player.objects.create(
                name=f"Player {i+1}",
                team=self.team,
                b_game=10.0,
                pa=40 + i,
                hit=10 + i,
                home_run=1 + (i % 3),
                walk=2 + (i % 2),
            )
            self.players.append(p)

        User = get_user_model()
        self.creator = User.objects.create_user(username="creator",
                                                password="pw")

    def test_handle_lineup_save_validation_failures(self):
        """Test handle_lineup_save with validation exception and False
          return."""
        from lineups.services.lineup_creation_handler import handle_lineup_save
        from lineups.services.input_data import LineupPlayerInput
        from lineups.services.exceptions import DomainError
        from unittest.mock import patch
        validated_data = {
            "team": self.team,
            "players": self.players,
            "created_by_id": self.creator.id,
            "original_players": [
                LineupPlayerInput(player_id=p.id, batting_order=idx + 1)
                for idx, p in enumerate(self.players)
            ],
            "name": "Test Lineup",
        }
        original_batting_orders = [idx + 1 for idx in range(9)]
        # Test validation exception
        with patch('lineups.services.lineup_creation_handler.\
        validate_lineup_model') as mock_validate:
            mock_validate.side_effect = Exception("Test validation error")
            with self.assertRaises(DomainError) as cm:
                handle_lineup_save(validated_data, original_batting_orders)
            self.assertIn("Test validation error", str(cm.exception))
        # Test validation returns False
        with patch('lineups.services.lineup_creation_handler.\
        validate_lineup_model') as mock_validate:
            mock_validate.return_value = False
            with self.assertRaises(DomainError) as cm:
                handle_lineup_save(validated_data, original_batting_orders)
            self.assertIn("Lineup validation failed", str(cm.exception))

    def test_generate_suggested_lineup_empty_or_none_result(self):
        """Test generate_suggested_lineup returns empty list for
        empty tuple or None from algorithm."""
        from lineups.interactor import LineupCreationInteractor
        from unittest.mock import patch
        interactor = LineupCreationInteractor()
        # Test with empty tuple
        with patch('lineups.interactor.algorithm_create_lineup') as mock_algo:
            mock_algo.return_value = tuple()
            result = interactor.generate_suggested_lineup(
                self.team.id,
                [p.id for p in self.players])
            self.assertEqual(result, [])
        # Test with None
        with patch('lineups.interactor.algorithm_create_lineup') as mock_algo:
            mock_algo.return_value = None
            result = interactor.generate_suggested_lineup(
                self.team.id,
                [p.id for p in self.players])
            self.assertEqual(result, [])


class AuthUserServiceTests(TestCase):
    """Unit tests for auth_user service functions."""

    def setUp(self):
        self.team = Team.objects.create()
        User = get_user_model()
        self.creator = User.objects.create_user(username="creator",
                                                password="pw")
        self.other = User.objects.create_user(username="other", password="pw")
        self.superuser = User.objects.create_superuser(username="admin",
                                                       password="pw")

    def test_authorize_lineup_deletion_all_scenarios(self):
        """Test authorize_lineup_deletion for all user types and
          permissions."""
        from lineups.services.auth_user import authorize_lineup_deletion
        from django.contrib.auth.models import AnonymousUser
        lineup = Lineup.objects.create(team=self.team, created_by=self.creator)
        # Test creator allowed
        result = authorize_lineup_deletion(self.creator, lineup)
        self.assertIsNone(result)
        # Test other user denied
        result = authorize_lineup_deletion(self.other, lineup)
        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, 403)
        self.assertIn("do not have permission", str(result.data))
        # Test superuser allowed
        result = authorize_lineup_deletion(self.superuser, lineup)
        self.assertIsNone(result)
        # Test unauthenticated denied
        result = authorize_lineup_deletion(AnonymousUser(), lineup)
        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, 401)
        self.assertIn("Authentication required", str(result.data))


class LineupViewEdgeCaseTests(TestCase):
    """Tests for edge cases in views.py to achieve 100% coverage."""

    def setUp(self):
        self.team = Team.objects.create()
        User = get_user_model()
        self.creator = User.objects.create_user(username="creator",
                                                password="pw")
        self.client = APIClient()

    def test_algorithm_generation_without_team_id(self):
        """Test algorithm generation path when team_id is None (line 116)."""
        # This is a defensive check - serializer should catch it, but test
        # the view logic
        self.client.force_authenticate(user=self.creator)
        # Manually construct a payload that bypasses serializer validation
        # by posting with empty players (triggers algorithm path)
        from unittest.mock import patch
        # Patch the serializer to allow None team_id through
        with patch('lineups.views.LineupCreate') as MockSerializer:
            mock_instance = MockSerializer.return_value
            mock_instance.is_valid.return_value = True
            mock_instance.validated_data = {
                "team_id": None,  # None team_id
                "players": []
            }
            resp = self.client.post("/api/v1/lineups/", {}, format="json")
            self.assertEqual(resp.status_code, 400)
            self.assertIn("team_id is required", str(resp.data))

    def test_views_extract_player_ids_with_non_list(self):
        """Test views.py line 120: _extract_player_ids returns None
        for non-list."""
        from lineups.views import LineupCreateView
        view = LineupCreateView()
        # Test with non-list input (e.g., None, string, int)
        result = view._extract_player_ids({"players": None})
        self.assertIsNone(result)
        result = view._extract_player_ids({"players": "not_a_list"})
        self.assertIsNone(result)
        result = view._extract_player_ids({"players": 123})
        self.assertIsNone(result)


class LineupInteractorTests(TestCase):
    """Additional tests to achieve 100% code coverage."""

    def setUp(self):
        self.team = Team.objects.create()
        self.players = []
        for i in range(9):
            p = Player.objects.create(
                name=f"Player {i+1}",
                team=self.team,
                b_game=10.0,
                pa=40 + i,
                hit=10 + i,
                home_run=1 + (i % 3),
                walk=2 + (i % 2),
            )
            self.players.append(p)
        User = get_user_model()
        self.creator = User.objects.create_user(username="creator",
                                                password="pw")

    def test_generate_suggested_lineup_none_team_id(self):
        """Test interactor.py line 64: team_id is None raises DomainError."""
        from lineups.interactor import LineupCreationInteractor
        from lineups.services.exceptions import DomainError
        interactor = LineupCreationInteractor()
        with self.assertRaises(DomainError) as cm:
            interactor.generate_suggested_lineup(None,
                                                 selected_player_ids=[1, 2, 3])
        self.assertIn("team_id is required", str(cm.exception))


class LineupDatabaseTests(TestCase):
    """Tests for database access layer functionality."""
    def setUp(self):
        self.team = Team.objects.create()
        self.players = []
        for i in range(9):
            p = Player.objects.create(
                name=f"Player {i+1}",
                team=self.team,
                b_game=10.0,
                pa=40 + i,
                hit=10 + i,
                home_run=1 + (i % 3),
                walk=2 + (i % 2),
            )
            self.players.append(p)
        User = get_user_model()
        self.creator = User.objects.create_user(username="creator",
                                                password="pw")

    def test_fetch_lineup_data_with_optional_fields(self):
        """Test fetch_lineup_data handles optional fields correctly."""
        from lineups.services.databa_access import fetch_lineup_data
        from lineups.services.input_data import (
            CreateLineupInput, LineupPlayerInput
            )
        # Test with all fields provided
        payload_full = CreateLineupInput(
            team_id=self.team.id,
            players=[LineupPlayerInput(player_id=p.id) for p in self.players],
            requested_user_id=self.creator.id,
        )
        result = fetch_lineup_data(payload_full)
        self.assertEqual(result["team"].id, self.team.id)
        self.assertEqual(len(result["players"]), 9)
        # Test with minimal payload (None optional fields)
        payload_minimal = CreateLineupInput(
            team_id=self.team.id,
            players=[LineupPlayerInput(player_id=p.id) for p in self.players],
            requested_user_id=None,
            name=None,
        )
        result = fetch_lineup_data(payload_minimal)
        self.assertIsNone(result["name"])
        self.assertIsNone(result["created_by_id"])
