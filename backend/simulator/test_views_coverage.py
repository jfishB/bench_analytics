from unittest.mock import MagicMock, patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from simulator.services.dto import SimulationResult
from simulator.views import _handle_simulation_request


class SimulatorViewsCoverageTest(TestCase):
    """Targeted tests for simulator/views.py coverage."""

    def setUp(self):
        self.client = APIClient()

    @patch("simulator.views.SimulationService")
    def test_handle_simulation_request_empty_results(self, mock_service_cls):
        """Test _handle_simulation_request when simulation returns no scores."""
        # Setup mock service
        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service

        # Setup mock result with empty scores
        mock_result = MagicMock()
        mock_result.all_scores = []  # Empty list triggers the error
        mock_service.run_simulation_flow.return_value = mock_result

        # Call the helper directly
        response = _handle_simulation_request([1, 2, 3], 100, "ids")

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Simulation produced no results", response.data["error"])

    @patch("simulator.views.SimulationService")
    def test_handle_simulation_request_unexpected_error(self, mock_service_cls):
        """Test _handle_simulation_request when an unexpected exception occurs."""
        # Setup mock to raise generic exception
        mock_service = MagicMock()
        mock_service_cls.return_value = mock_service
        mock_service.run_simulation_flow.side_effect = Exception("Unexpected boom")

        # Call the helper directly
        response = _handle_simulation_request([1, 2, 3], 100, "ids")

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("An unexpected error occurred", response.data["error"])
        self.assertIn("Unexpected boom", response.data["detail"])

    def test_simulate_by_player_names_invalid_serializer(self):
        """Test simulate_by_player_names with invalid data."""
        # Missing player_names
        data = {"num_games": 100}
        
        # We need to authenticate since the view requires it
        # But for unit testing the view function directly or via client?
        # Let's use the client and force authentication if possible, or just mock the permission?
        # The simplest way to test serializer validation failure in the view is to send bad data.
        
        # We need a user to authenticate
        from django.contrib.auth.models import User
        user = User.objects.create_user(username="testuser", password="password")
        self.client.force_authenticate(user=user)

        url = "/api/v1/simulator/simulate-by-names/"
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("player_names", response.data)

    def test_simulate_by_team_invalid_serializer(self):
        """Test simulate_by_team with invalid data."""
        # Missing team_id
        data = {"num_games": 100}
        
        from django.contrib.auth.models import User
        user = User.objects.create_user(username="testuser2", password="password")
        self.client.force_authenticate(user=user)

        url = "/api/v1/simulator/simulate-by-team/"
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("team_id", response.data)
