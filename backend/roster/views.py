from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Team, Player
from .serializer import (
    TeamSerializer, 
    PlayerSerializer, 
    PlayerListSerializer,
    PlayerRankedSerializer,
    PlayerCreateSerializer,
    PlayerPartialUpdateSerializer,
    PlayerRankQuerySerializer
)
from .services.player_ranking import (
    get_ranked_players,
    create_player_with_stats,
    update_player_stats,
    get_team_by_id
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
    Keeps views thin - delegates business logic to services.
    """
    queryset = Player.objects.select_related('team').all()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return PlayerCreateSerializer
        elif self.action == 'partial_update':
            return PlayerPartialUpdateSerializer
        elif self.action == 'list':
            return PlayerListSerializer
        elif self.action == 'ranked':
            return PlayerRankedSerializer
        return PlayerSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new player with validation.
        Delegates to service layer for business logic.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Service layer handles creation
        player = create_player_with_stats(**serializer.validated_data)
        
        output_serializer = PlayerSerializer(player)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Update player stats.
        Delegates to service layer for business logic.
        """
        player = self.get_object()
        serializer = self.get_serializer(player, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Service layer handles updates
        updated_player = update_player_stats(player.id, **serializer.validated_data)
        
        output_serializer = PlayerSerializer(updated_player)
        return Response(output_serializer.data)
    
    @action(detail=False, methods=['get'], url_path='ranked')
    def ranked(self, request):
        """
        Custom endpoint: GET /api/v1/roster/players/ranked/
        Returns players sorted by WOS score.
        
        Query params validated via PlayerRankQuerySerializer.
        Business logic delegated to service layer.
        """
        # Validate query parameters
        query_serializer = PlayerRankQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        
        ascending = query_serializer.validated_data.get('ascending', False)
        top_n = query_serializer.validated_data.get('top', None)
        
        # Service layer handles ranking logic
        ranked_players = get_ranked_players(ascending=ascending, top_n=top_n)
        
        serializer = PlayerRankedSerializer(ranked_players, many=True)
        return Response({"players": serializer.data})

