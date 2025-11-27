from datetime import date, timedelta
from typing import Dict, Iterable, Optional

from ..models.clients import Client, ClientCreate

from abc import ABC, abstractmethod

class abc_ClientService(ABC):
    @abstractmethod
    async def list_clients(self) -> Iterable[Client]:...
    @abstractmethod
    async def get_client(self, client_id) -> Optional[Client]:...
    @abstractmethod
    async def create_client(self, request : ClientCreate) -> Client:...

#waiting concrete implementation
class ClientService(abc_ClientService):
    async def list_clients(self) -> Iterable[Client]:...
    async def get_client(self, client_id) -> Optional[Client]:...
    async def create_client(self, request : ClientCreate) -> Client:...

class MockClientService(abc_ClientService):
    def __init__(self):
        today = date.today()
        self._clients: Dict[int, Client] = {
            1: Client(id=1, full_name="Celia Client", email="celia@example.com", membership_level="Gold", last_visit=today),
            2: Client(
                id=2, full_name="Peter Patron", email="peter@example.com", membership_level="Platinum", last_visit=today - timedelta(days=5)
            ),
        }
        self._sequence = max(self._clients.keys())

    async def list_clients(self) -> Iterable[Client]:
        return sorted(self._clients.values(), key=lambda client: client.full_name)

    async def get_client(self, client_id: int) -> Optional[Client]:
        return self._clients.get(client_id)

    async def create_client(self, request: ClientCreate) -> Client:
        self._sequence += 1
        client = Client(id=self._sequence, **request.model_dump(), last_visit=None)
        self._clients[self._sequence] = client
        return client
