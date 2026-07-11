from app.inventory import Inventory, PetProfileRegistry
from app.perception import PerceptionService


class ScannerFake:
    def scan(self):
        return ()


class BuilderFake:
    def __init__(self) -> None:
        self.received = None

    def build(self, detections):
        self.received = detections
        return Inventory()


def test_perception_service_builds_inventory() -> None:
    builder = BuilderFake()
    registry = PetProfileRegistry()

    service = PerceptionService(
        scanner=ScannerFake(),
        inventory_builder=builder,
        registry=registry,
    )

    inventory = service.build_inventory()

    assert isinstance(inventory, Inventory)
    assert builder.received == ()
    assert service.registry is registry