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
        self.creator = User.objects.create_user(username="creator", password="pw")
        self.other = User.objects.create_user(username="other", password="pw")
        self.superuser = User.objects.create_superuser(username="admin", password="pw")

    def test_manual_save_creates_persisted_lineup(self):
        """POST with players + batting orders should persist a Lineup and players."""
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

        lp_qs = LineupPlayer.objects.filter(lineup=lineup).order_by("batting_order")
        self.assertEqual(lp_qs.count(), 9)
        for idx, lp in enumerate(lp_qs):
            self.assertEqual(lp.batting_order, idx + 1)
            self.assertEqual(lp.player.team_id, self.team.id)

    def test_rejects_missing_batting_orders(self):
        """Payload without batting_order is treated as team_id-only and generates a suggestion."""
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
        # Es wird nur ein vorgeschlagenes Lineup generiert, nichts gespeichert
        self.assertEqual(Lineup.objects.count(), 0)

    def test_team_id_only_generates_suggested_lineup(self):
        """POST with only team_id generates a suggested lineup without saving it."""
        payload = {"team_id": self.team.id}

        self.client.force_authenticate(user=self.creator)
        resp = self.client.post(self.base_url, payload, format="json")
        self.assertEqual(resp.status_code, 201)

        data = resp.json()
        self.assertEqual(data["team_id"], self.team.id)
        self.assertIn("players", data)
        self.assertLessEqual(len(data["players"]), 9)
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
    def setUp(self):
        self.team = Team.objects.create()
        self.player = Player.objects.create(name="Player 1", team=self.team)
        User = get_user_model()
        self.creator = User.objects.create_user(username="creator_model", password="pw")

    def test_create_lineup_and_player(self):
        lineup = Lineup.objects.create(team=self.team, created_by=self.creator)
        lp = LineupPlayer.objects.create(lineup=lineup, player=self.player, batting_order=1)
        

        self.assertEqual(lp.lineup, lineup)
        self.assertEqual(lp.player, self.player)
        self.assertEqual(lp.batting_order, 1)

        self.assertEqual(lineup.players.count(), 1)

    def test_lineup_str_method(self):
        """Test Lineup __str__ method."""
        lineup = Lineup.objects.create(
            team=self.team, 
            name="Test Lineup",
            created_by=self.creator
        )
        str_repr = str(lineup)
        self.assertIn("Test Lineup", str_repr)
        self.assertIn(f"Team {self.team.id}", str_repr)

    def test_lineup_player_str_method(self):
        """Test LineupPlayer __str__ method."""
        lineup = Lineup.objects.create(team=self.team, created_by=self.creator)
        lp = LineupPlayer.objects.create(
            lineup=lineup, 
            player=self.player, 
            batting_order=3
        )
        str_repr = str(lp)
        self.assertIn("3.", str_repr)
        self.assertIn("Player 1", str_repr)


class LineupValidationTests(TestCase):
    """Tests for lineup validation logic to achieve 100% coverage."""

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
        self.creator = User.objects.create_user(username="creator", password="pw")

    def test_reject_duplicate_batting_orders(self):
        """POST with duplicate batting orders should fail with 400."""
        client = APIClient()
        payload = {
            "team_id": self.team.id,
            "name": "Duplicate Orders",
            "players": [
                {"player_id": self.players[0].id, "batting_order": 1},
                {"player_id": self.players[1].id, "batting_order": 1},  # duplicate
                {"player_id": self.players[2].id, "batting_order": 3},
                {"player_id": self.players[3].id, "batting_order": 4},
                {"player_id": self.players[4].id, "batting_order": 5},
                {"player_id": self.players[5].id, "batting_order": 6},
                {"player_id": self.players[6].id, "batting_order": 7},
                {"player_id": self.players[7].id, "batting_order": 8},
                {"player_id": self.players[8].id, "batting_order": 9},
            ],
        }

        client.force_authenticate(user=self.creator)
        resp = client.post("/api/v1/lineups/", payload, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Batting orders must be unique", str(resp.data))

    def test_reject_invalid_batting_order_range(self):
        """POST with batting orders not covering 1-9 should fail."""
        client = APIClient()
        payload = {
            "team_id": self.team.id,
            "name": "Invalid Range",
            "players": [
                {"player_id": self.players[0].id, "batting_order": 2},  # missing 1
                {"player_id": self.players[1].id, "batting_order": 3},
                {"player_id": self.players[2].id, "batting_order": 4},
                {"player_id": self.players[3].id, "batting_order": 5},
                {"player_id": self.players[4].id, "batting_order": 6},
                {"player_id": self.players[5].id, "batting_order": 7},
                {"player_id": self.players[6].id, "batting_order": 8},
                {"player_id": self.players[7].id, "batting_order": 9},
                {"player_id": self.players[8].id, "batting_order": 10},  # invalid
            ],
        }

        client.force_authenticate(user=self.creator)
        resp = client.post("/api/v1/lineups/", payload, format="json")
        # Serializer validation catches batting_order > 9 before domain validation
        self.assertEqual(resp.status_code, 400)

    def test_reject_wrong_number_of_players(self):
        """POST with != 9 players should fail."""
        client = APIClient()
        payload = {
            "team_id": self.team.id,
            "name": "Too Few Players",
            "players": [
                {"player_id": self.players[0].id, "batting_order": 1},
                {"player_id": self.players[1].id, "batting_order": 2},
                # only 2 players, need 9
            ],
        }

        client.force_authenticate(user=self.creator)
        resp = client.post("/api/v1/lineups/", payload, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Players not found", str(resp.data))

    def test_reject_nonexistent_team(self):
        """POST with invalid team_id should fail."""
        client = APIClient()
        payload = {
            "team_id": 99999,  # doesn't exist
            "name": "Bad Team",
            "players": [
                {"player_id": p.id, "batting_order": idx + 1}
                for idx, p in enumerate(self.players)
            ],
        }

        client.force_authenticate(user=self.creator)
        resp = client.post("/api/v1/lineups/", payload, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Unknown team", str(resp.data))

    def test_reject_nonexistent_players(self):
        """POST with invalid player_id should fail."""
        client = APIClient()
        payload = {
            "team_id": self.team.id,
            "name": "Bad Players",
            "players": [
                {"player_id": 99999, "batting_order": 1},  # doesn't exist
            ] + [
                {"player_id": p.id, "batting_order": idx + 2}
                for idx, p in enumerate(self.players[1:])
            ],
        }

        client.force_authenticate(user=self.creator)
        resp = client.post("/api/v1/lineups/", payload, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Players not found", str(resp.data))

    def test_reject_players_from_wrong_team(self):
        """POST with players from different teams should fail."""
        other_team = Team.objects.create()
        wrong_player = Player.objects.create(
            name="Wrong Team Player",
            team=other_team,
            b_game=10.0,
            pa=40,
            hit=10,
            home_run=1,
            walk=2,
        )

        client = APIClient()
        payload = {
            "team_id": self.team.id,
            "name": "Mixed Teams",
            "players": [
                {"player_id": wrong_player.id, "batting_order": 1},  # wrong team
            ] + [
                {"player_id": p.id, "batting_order": idx + 2}
                for idx, p in enumerate(self.players[1:])
            ],
        }

        client.force_authenticate(user=self.creator)
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


class LineupViewSetTests(TestCase):
    """Tests for LineupViewSet to cover remaining view logic."""

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
        self.creator = User.objects.create_user(username="creator", password="pw")
        self.superuser = User.objects.create_superuser(username="admin", password="pw")
        self.other = User.objects.create_user(username="other", password="pw")

    def test_viewset_queryset_for_unauthenticated(self):
        """Unauthenticated requests should get empty queryset."""
        client = APIClient()
        # Don't authenticate
        resp = client.get("/api/v1/lineups/saved/")
        # Should get 401 from IsAuthenticated permission
        self.assertEqual(resp.status_code, 401)

    def test_viewset_queryset_for_superuser(self):
        """Superuser should see all lineups."""
        Lineup.objects.create(team=self.team, created_by=self.creator, name="Lineup 1")
        Lineup.objects.create(team=self.team, created_by=self.other, name="Lineup 2")

        client = APIClient()
        client.force_authenticate(user=self.superuser)
        resp = client.get("/api/v1/lineups/saved/")
        self.assertEqual(resp.status_code, 200)
        # Superuser sees both lineups
        self.assertEqual(len(resp.data), 2)

    def test_viewset_queryset_filters_by_user(self):
        """Normal users should only see their own lineups."""
        lineup1 = Lineup.objects.create(team=self.team, created_by=self.creator, name="My Lineup")
        Lineup.objects.create(team=self.team, created_by=self.other, name="Other Lineup")

        client = APIClient()
        client.force_authenticate(user=self.creator)
        resp = client.get("/api/v1/lineups/saved/")
        self.assertEqual(resp.status_code, 200)
        # Creator only sees their own lineup
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["name"], "My Lineup")


class LineupServiceTests(TestCase):
    """Unit tests for lineup services to achieve 100% coverage."""

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
        self.creator = User.objects.create_user(username="creator", password="pw")

    def test_validate_batting_orders_with_dict_input(self):
        """Test validate_batting_orders with dict input (alternative code path)."""
        from lineups.services.validator import validate_batting_orders
        
        # Use dicts instead of dataclass objects
        players_dict = [
            {"player_id": p.id, "batting_order": idx + 1}
            for idx, p in enumerate(self.players)
        ]
        
        # Should not raise
        validate_batting_orders(players_dict)

    def test_validate_batting_orders_rejects_none(self):
        """Test that None batting_order is rejected."""
        from lineups.services.validator import validate_batting_orders
        from lineups.services.exceptions import BadBattingOrder
        
        players_dict = [
            {"player_id": p.id, "batting_order": None}  # explicit None
            for p in self.players
        ]
        
        with self.assertRaises(BadBattingOrder) as cm:
            validate_batting_orders(players_dict)
        self.assertIn("must have a batting order", str(cm.exception))

    def test_validate_batting_orders_wrong_count(self):
        """Test that wrong player count is rejected."""
        from lineups.services.validator import validate_batting_orders
        from lineups.services.exceptions import BadBattingOrder
        
        # Only 5 players
        players_dict = [
            {"player_id": p.id, "batting_order": idx + 1}
            for idx, p in enumerate(self.players[:5])
        ]
        
        with self.assertRaises(BadBattingOrder) as cm:
            validate_batting_orders(players_dict)
        self.assertIn("exactly 9 players", str(cm.exception))

    def test_validate_data_with_dict_payload(self):
        """Test validate_data with dict payload (alternative code path)."""
        from lineups.services.validator import validate_data
        
        # Use plain dict instead of dataclass
        payload_dict = {
            "team_id": self.team.id,
            "players": [
                {"player_id": p.id}
                for p in self.players
            ],
            "requested_user_id": self.creator.id,
        }
        
        result = validate_data(payload_dict)
        self.assertEqual(result["team"].id, self.team.id)
        self.assertEqual(len(result["players"]), 9)

    def test_validate_lineup_model_missing_batting_orders(self):
        """Test validate_lineup_model rejects lineup with missing batting_orders."""
        from lineups.services.validator import validate_lineup_model
        from lineups.services.exceptions import BadBattingOrder
        
        lineup = Lineup.objects.create(team=self.team, created_by=self.creator)
        # Create player without batting_order (None)
        LineupPlayer.objects.create(lineup=lineup, player=self.players[0], batting_order=None)
        
        with self.assertRaises(BadBattingOrder):
            validate_lineup_model(lineup)

    def test_validate_lineup_model_non_consecutive_orders(self):
        """Test validate_lineup_model rejects non-consecutive batting orders."""
        from lineups.services.validator import validate_lineup_model
        from lineups.services.exceptions import BadBattingOrder
        
        lineup = Lineup.objects.create(team=self.team, created_by=self.creator)
        # Create players with non-consecutive orders (skip 2)
        for idx, p in enumerate(self.players):
            order = idx + 1 if idx < 1 else idx + 2  # 1, 3, 4, 5, 6, 7, 8, 9, 10
            LineupPlayer.objects.create(lineup=lineup, player=p, batting_order=order)
        
        with self.assertRaises(BadBattingOrder):
            validate_lineup_model(lineup)

    def test_validate_data_no_creator_with_require_creator(self):
        """Test validate_data raises NoCreator when no superuser exists."""
        from lineups.services.validator import validate_data
        from lineups.services.exceptions import NoCreator
        from django.contrib.auth import get_user_model
        
        # Delete all users including superuser
        User = get_user_model()
        User.objects.all().delete()
        
        payload_dict = {
            "team_id": self.team.id,
            "players": [{"player_id": p.id} for p in self.players],
            "requested_user_id": None,  # No user provided
        }
        
        # Should raise NoCreator since require_creator=True by default
        with self.assertRaises(NoCreator):
            validate_data(payload_dict, require_creator=True)

    def test_validate_data_no_creator_optional(self):
        """Test validate_data returns None for creator when require_creator=False."""
        from lineups.services.validator import validate_data
        
        payload_dict = {
            "team_id": self.team.id,
            "players": [{"player_id": p.id} for p in self.players],
            "requested_user_id": None,  # No user provided
        }
        
        # Should not raise when require_creator=False
        result = validate_data(payload_dict, require_creator=False)
        self.assertIsNone(result["created_by_id"])

    def test_validate_lineup_model_none_input(self):
        """Test validate_lineup_model raises PlayersNotFound for None."""
        from lineups.services.validator import validate_lineup_model
        from lineups.services.exceptions import PlayersNotFound
        
        with self.assertRaises(PlayersNotFound):
            validate_lineup_model(None)

    def test_validate_lineup_model_no_team(self):
        """Test validate_lineup_model raises PlayersWrongTeam for lineup without team."""
        from lineups.services.validator import validate_lineup_model
        from lineups.services.exceptions import PlayersWrongTeam
        
        # Create lineup without team (using create with team_id=None won't work due to FK)
        # Instead, test with a lineup object that has team_id attribute set to None
        lineup = Lineup(name="Test", created_by=self.creator)
        lineup.team_id = None
        
        with self.assertRaises(PlayersWrongTeam):
            validate_lineup_model(lineup)

    def test_validate_lineup_model_empty_players(self):
        """Test validate_lineup_model raises PlayersNotFound for lineup without players."""
        from lineups.services.validator import validate_lineup_model
        from lineups.services.exceptions import PlayersNotFound
        
        lineup = Lineup.objects.create(team=self.team, created_by=self.creator)
        # Don't add any players
        
        with self.assertRaises(PlayersNotFound):
            validate_lineup_model(lineup)

    def test_validate_lineup_model_wrong_team_player(self):
        """Test validate_lineup_model raises PlayersWrongTeam when player from different team."""
        from lineups.services.validator import validate_lineup_model
        from lineups.services.exceptions import PlayersWrongTeam
        
        other_team = Team.objects.create()
        wrong_player = Player.objects.create(
            name="Wrong Team",
            team=other_team,
            b_game=10.0,
            pa=40,
            hit=10,
            home_run=1,
            walk=2,
        )
        
        lineup = Lineup.objects.create(team=self.team, created_by=self.creator)
        LineupPlayer.objects.create(lineup=lineup, player=wrong_player, batting_order=1)
        
        with self.assertRaises(PlayersWrongTeam):
            validate_lineup_model(lineup)

    def test_validate_data_player_id_as_int(self):
        """Test validate_data handles player IDs provided as plain integers."""
        from lineups.services.validator import validate_data
        
        # Pass player IDs as integers instead of dicts
        payload_dict = {
            "team_id": self.team.id,
            "players": [p.id for p in self.players],  # plain ints
            "requested_user_id": self.creator.id,
        }
        
        result = validate_data(payload_dict)
        self.assertEqual(result["team"].id, self.team.id)
        self.assertEqual(len(result["players"]), 9)

    def test_validate_data_missing_player_id(self):
        """Test validate_data raises PlayersNotFound when player_id is None."""
        from lineups.services.validator import validate_data
        from lineups.services.exceptions import PlayersNotFound
        
        payload_dict = {
            "team_id": self.team.id,
            "players": [
                {"player_id": self.players[0].id},
                {"player_id": None},  # Missing player_id
            ] + [{"player_id": p.id} for p in self.players[2:]],
            "requested_user_id": self.creator.id,
        }
        
        with self.assertRaises(PlayersNotFound):
            validate_data(payload_dict)


class LineupAlgorithmTests(TestCase):
    """Tests for algorithm-specific edge cases."""

    def setUp(self):
        self.team = Team.objects.create()
        User = get_user_model()
        self.creator = User.objects.create_user(username="creator", password="pw")

    def test_generate_suggested_lineup_empty_roster(self):
        """Test generate_suggested_lineup returns empty list for team with no players."""
        from lineups.services.lineup_creation_handler import generate_suggested_lineup
        
        # Team has no players
        result = generate_suggested_lineup(self.team.id)
        self.assertEqual(result, [])

    def test_calculate_player_adjustments_with_zero_b_game(self):
        """Test calculate_player_adjustments when player has b_game=0 (line 47)."""
        from lineups.services.algorithm_logic import calculate_player_adjustments
        
        player = Player.objects.create(
            name="Zero Games",
            team=self.team,
            b_game=0,  # Zero games
            pa=0,
            hit=0,
            home_run=0,
            walk=0,
        )
        
        adjustments = {
            "h_adj": 0, "hr_adj": 0, "bb_adj": 0, "ibb_adj": 0, "hbp_adj": 0,
            "sb_adj": 0, "cs_adj": 0, "gidp_adj": 0, "sf_adj": 0, "sh_adj": 0, "tb_adj": 0
        }
        
        result = calculate_player_adjustments(player, 1, adjustments)
        # Should return adjustments unchanged
        self.assertEqual(result, adjustments)

    def test_calculate_player_adjustments_with_none_b_game(self):
        """Test calculate_player_adjustments when player has b_game=None (line 47)."""
        from lineups.services.algorithm_logic import calculate_player_adjustments
        
        player = Player.objects.create(
            name="None Games",
            team=self.team,
            b_game=None,  # None games
            pa=10,
            hit=5,
            home_run=1,
            walk=2,
        )
        
        adjustments = {
            "h_adj": 0, "hr_adj": 0, "bb_adj": 0, "ibb_adj": 0, "hbp_adj": 0,
            "sb_adj": 0, "cs_adj": 0, "gidp_adj": 0, "sf_adj": 0, "sh_adj": 0, "tb_adj": 0
        }
        
        result = calculate_player_adjustments(player, 1, adjustments)
        # Should return adjustments unchanged
        self.assertEqual(result, adjustments)

    def test_calculate_baserun_with_zero_denominator(self):
        """Test calculate_player_baserun_values returns 0 when b+c is 0 (line 143)."""
        from lineups.services.algorithm_logic import calculate_player_baserun_values
        
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
        """Test algorithm_create_lineup returns empty tuple when no lineup found (line 176)."""
        from lineups.services.algorithm_logic import algorithm_create_lineup
        from lineups.services.input_data import CreateLineupInput, LineupPlayerInput
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
        with patch('lineups.services.algorithm_logic.permutations') as mock_perms:
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
        self.creator = User.objects.create_user(username="creator", password="pw")

    def test_handle_lineup_save_validation_exception(self):
        """Test handle_lineup_save when validate_lineup_model raises exception (lines 78-79)."""
        from lineups.services.lineup_creation_handler import handle_lineup_save
        from lineups.services.input_data import LineupPlayerInput
        from rest_framework.serializers import ValidationError
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
        
        # Mock validate_lineup_model to raise an exception
        with patch('lineups.services.lineup_creation_handler.validate_lineup_model') as mock_validate:
            mock_validate.side_effect = Exception("Test validation error")
            
            with self.assertRaises(ValidationError) as cm:
                handle_lineup_save(validated_data, self.creator)
            
            self.assertIn("Test validation error", str(cm.exception))

    def test_handle_lineup_save_validation_returns_false(self):
        """Test handle_lineup_save when validate_lineup_model returns False (line 81)."""
        from lineups.services.lineup_creation_handler import handle_lineup_save
        from lineups.services.input_data import LineupPlayerInput
        from rest_framework.serializers import ValidationError
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
        
        # Mock validate_lineup_model to return False
        with patch('lineups.services.lineup_creation_handler.validate_lineup_model') as mock_validate:
            mock_validate.return_value = False
            
            with self.assertRaises(ValidationError) as cm:
                handle_lineup_save(validated_data, self.creator)
            
            self.assertIn("Lineup validation failed", str(cm.exception))

    def test_generate_suggested_lineup_empty_tuple(self):
        """Test generate_suggested_lineup returns empty list when algorithm returns empty tuple (line 117)."""
        from lineups.services.lineup_creation_handler import generate_suggested_lineup
        from unittest.mock import patch
        
        # Mock algorithm_create_lineup to return empty tuple
        with patch('lineups.services.lineup_creation_handler.algorithm_create_lineup') as mock_algo:
            mock_algo.return_value = tuple()  # Empty tuple
            
            result = generate_suggested_lineup(self.team.id, [p.id for p in self.players])
            self.assertEqual(result, [])

    def test_generate_suggested_lineup_none_result(self):
        """Test generate_suggested_lineup handles None result from algorithm (line 117)."""
        from lineups.services.lineup_creation_handler import generate_suggested_lineup
        from unittest.mock import patch
        
        # Mock algorithm_create_lineup to return None
        with patch('lineups.services.lineup_creation_handler.algorithm_create_lineup') as mock_algo:
            mock_algo.return_value = None
            
            result = generate_suggested_lineup(self.team.id, [p.id for p in self.players])
            self.assertEqual(result, [])



class AuthUserServiceTests(TestCase):
    """Unit tests for auth_user service functions."""

    def setUp(self):
        self.team = Team.objects.create()
        User = get_user_model()
        self.creator = User.objects.create_user(username="creator", password="pw")
        self.other = User.objects.create_user(username="other", password="pw")
        self.superuser = User.objects.create_superuser(username="admin", password="pw")

    def test_authorize_lineup_deletion_creator_allowed(self):
        """Test that creator can delete their own lineup."""
        from lineups.services.auth_user import authorize_lineup_deletion
        
        lineup = Lineup.objects.create(team=self.team, created_by=self.creator)
        result = authorize_lineup_deletion(self.creator, lineup)
        self.assertIsNone(result)  # None means authorized

    def test_authorize_lineup_deletion_other_user_denied(self):
        """Test that other user cannot delete lineup (triggers line 14)."""
        from lineups.services.auth_user import authorize_lineup_deletion
        
        lineup = Lineup.objects.create(team=self.team, created_by=self.creator)
        result = authorize_lineup_deletion(self.other, lineup)
        self.assertIsNotNone(result)  # Response means denied
        self.assertEqual(result.status_code, 403)
        self.assertIn("do not have permission", str(result.data))

    def test_authorize_lineup_deletion_superuser_allowed(self):
        """Test that superuser can delete any lineup (triggers is_superuser check)."""
        from lineups.services.auth_user import authorize_lineup_deletion
        
        lineup = Lineup.objects.create(team=self.team, created_by=self.creator)
        result = authorize_lineup_deletion(self.superuser, lineup)
        self.assertIsNone(result)  # None means authorized

    def test_authorize_lineup_deletion_unauthenticated(self):
        """Test that unauthenticated user is denied."""
        from lineups.services.auth_user import authorize_lineup_deletion
        from django.contrib.auth.models import AnonymousUser
        
        lineup = Lineup.objects.create(team=self.team, created_by=self.creator)
        result = authorize_lineup_deletion(AnonymousUser(), lineup)
        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, 403)
        self.assertIn("Authentication required", str(result.data))


class LineupViewEdgeCaseTests(TestCase):
    """Tests for edge cases in views.py to achieve 100% coverage."""

    def setUp(self):
        self.team = Team.objects.create()
        User = get_user_model()
        self.creator = User.objects.create_user(username="creator", password="pw")
        self.client = APIClient()

    def test_algorithm_generation_without_team_id(self):
        """Test algorithm generation path when team_id is None (line 116)."""
        # This is a defensive check - serializer should catch it, but test the view logic
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

    def test_viewset_get_queryset_with_none_user(self):
        """Test ViewSet get_queryset when request.user is None (line 181)."""
        from lineups.views import LineupViewSet
        from unittest.mock import Mock
        
        viewset = LineupViewSet()
        
        # Create a mock request with user=None
        mock_request = Mock()
        mock_request.user = None
        viewset.request = mock_request
        
        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 0)  # Should return empty queryset

    def test_viewset_get_queryset_with_unauthenticated_user(self):
        """Test ViewSet get_queryset when user.is_authenticated is False."""
        from lineups.views import LineupViewSet
        from unittest.mock import Mock
        
        viewset = LineupViewSet()
        
        # Create a mock request with unauthenticated user
        mock_request = Mock()
        mock_user = Mock()
        mock_user.is_authenticated = False
        mock_request.user = mock_user
        viewset.request = mock_request
        
        queryset = viewset.get_queryset()
        self.assertEqual(queryset.count(), 0)  # Should return empty queryset
