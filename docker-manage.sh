#!/bin/bash

# Agnovat Analyst - Docker Management Script
# Easy commands to manage Docker deployment

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check docker-compose availability
if command -v docker-compose &> /dev/null; then
    DC="docker-compose"
else
    DC="docker compose"
fi

# Show usage
usage() {
    echo "Agnovat Analyst - Docker Management"
    echo ""
    echo "Usage: ./docker-manage.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start       Start the containers"
    echo "  stop        Stop the containers"
    echo "  restart     Restart the containers"
    echo "  logs        View container logs"
    echo "  status      Show container status"
    echo "  shell       Open shell in container"
    echo "  test        Test the server"
    echo "  rebuild     Rebuild and restart"
    echo "  clean       Stop and remove containers"
    echo "  help        Show this help"
    echo ""
}

# Commands
case "$1" in
    start)
        echo -e "${BLUE}🚀 Starting Agnovat Analyst...${NC}"
        $DC up -d
        sleep 3
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Server started successfully!${NC}"
            echo "   URL: http://localhost:8000"
        else
            echo -e "${RED}❌ Server failed to start${NC}"
            $DC logs --tail=20
        fi
        ;;

    stop)
        echo -e "${YELLOW}🛑 Stopping containers...${NC}"
        $DC stop
        echo -e "${GREEN}✅ Stopped${NC}"
        ;;

    restart)
        echo -e "${BLUE}🔄 Restarting containers...${NC}"
        $DC restart
        sleep 3
        echo -e "${GREEN}✅ Restarted${NC}"
        ;;

    logs)
        echo -e "${BLUE}📋 Container logs (Ctrl+C to exit):${NC}"
        $DC logs -f
        ;;

    status)
        echo -e "${BLUE}📊 Container Status:${NC}"
        $DC ps
        echo ""
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Server is healthy${NC}"
            curl -s http://localhost:8000/health | python3 -m json.tool
        else
            echo -e "${RED}❌ Server is not responding${NC}"
        fi
        ;;

    shell)
        echo -e "${BLUE}🐚 Opening shell in container...${NC}"
        docker exec -it agnovat-analyst /bin/bash
        ;;

    test)
        echo -e "${BLUE}🧪 Testing server...${NC}"
        echo ""
        echo "1. Health check:"
        curl -s http://localhost:8000/health | python3 -m json.tool
        echo ""
        echo "2. API docs available at:"
        echo "   http://localhost:8000/docs"
        echo ""
        echo "3. All endpoints:"
        curl -s http://localhost:8000/openapi.json | \
            python3 -c "import sys, json; paths = json.load(sys.stdin)['paths']; print(f'Total endpoints: {len(paths)}'); [print(f'  {p}') for p in sorted(paths.keys()) if p.startswith('/api/')]"
        ;;

    rebuild)
        echo -e "${BLUE}🔨 Rebuilding and restarting...${NC}"
        $DC down
        $DC build --no-cache
        $DC up -d
        sleep 3
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Rebuild successful!${NC}"
        else
            echo -e "${RED}❌ Rebuild failed${NC}"
            $DC logs --tail=20
        fi
        ;;

    clean)
        echo -e "${YELLOW}🧹 Stopping and removing containers...${NC}"
        $DC down -v
        echo -e "${GREEN}✅ Cleaned up${NC}"
        ;;

    help|"")
        usage
        ;;

    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        usage
        exit 1
        ;;
esac
