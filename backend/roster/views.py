from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Team, Player
from .serializer import (
    TeamSerializer, 
    PlayerSerializer, 
    PlayerListSerializer,
    PlayerRankedSerializer
)
from .services.player_ranking import (
    get_ranked_players,
    create_player_with_stats,
    update_player_stats
)


class TeamViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Team model.
    Provides CRUD operations for teams.
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


class PlayerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Player model.
    Provides CRUD operations plus custom ranking endpoint.
    """
    queryset = Player.objects.select_related('team').all()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return PlayerListSerializer
        elif self.action == 'ranked':
            return PlayerRankedSerializer
        return PlayerSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new player with validation."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Use service layer for creation
        player = create_player_with_stats(**serializer.validated_data)
        
        output_serializer = PlayerSerializer(player)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def partial_update(self, request, *args, **kwargs):
        """Update player stats using service layer."""
        player = self.get_object()
        serializer = self.get_serializer(player, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Use service layer for updates
        updated_player = update_player_stats(player.id, **serializer.validated_data)
        
        output_serializer = PlayerSerializer(updated_player)
        return Response(output_serializer.data)
    
    @action(detail=False, methods=['get'], url_path='ranked')
    def ranked(self, request):
        """
        Custom endpoint: GET /api/v1/roster/players/ranked/
        Returns players sorted by WOS score.
        
        Query params:
            - ascending: bool (default=false)
            - top: int (optional limit)
        """
        ascending = request.query_params.get('ascending', 'false').lower() == 'true'
        top_n = request.query_params.get('top', None)
        
        if top_n:
            try:
                top_n = int(top_n)
            except ValueError:
                return Response(
                    {"error": "Invalid 'top' parameter. Must be an integer."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Use service layer for ranking logic
        ranked_players = get_ranked_players(ascending=ascending, top_n=top_n)
        
        serializer = PlayerRankedSerializer(ranked_players, many=True)
        return Response({"players": serializer.data})

