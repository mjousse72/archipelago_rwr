try:
    from worlds.LauncherComponents import Component, Type, components, launch as launch_component

    def _launch_rwr_client(*args: str) -> None:
        from .client.rwr_client import main
        launch_component(main, name="RWRClient", args=args)

    components.append(Component(
        "RWR Client",
        func=_launch_rwr_client,
        component_type=Type.CLIENT,
    ))
except ImportError:
    pass  # Not running inside Archipelago (e.g., standalone tests)

try:
    from .world import RWRWorld as RWRWorld
except ImportError:
    pass  # worlds.AutoWorld not available outside Archipelago
