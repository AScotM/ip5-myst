import atexit
import curses
import json
import math
import os
import random
import signal
import subprocess
import sys
import threading
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple


class GlyphType(Enum):
    FLOW = "flow"
    PULSE = "pulse"
    WHISPER = "whisper"
    SHADOW = "shadow"
    ECHO = "echo"


@dataclass
class Glyph:
    type: GlyphType
    intensity: float
    position: Tuple[int, int]
    age: int = 0
    char: str = " "
    color_pair: int = 0


class NetworkEntity:
    def __init__(self, interface: str, rx_bytes: int, tx_bytes: int, sample_time: float):
        self.name = self._generate_spirit_name(interface)
        self.interface = interface
        self.rx_bytes = rx_bytes
        self.tx_bytes = tx_bytes
        self.rx_rate = 0.0
        self.tx_rate = 0.0
        self.essence = random.uniform(0.1, 1.0)
        self.aura = self._generate_aura()
        self.glyphs: List[Glyph] = []
        self.last_seen = sample_time
        self.last_sample_time = sample_time
        self.whispers: List[str] = []
        self.ips: List[str] = []
        self.last_ip_refresh = 0.0

    def _generate_spirit_name(self, interface: str) -> str:
        names = {
            "eth": ["Silent River", "Whispering Wind", "Ethereal Flow"],
            "en": ["Silent River", "Whispering Wind", "Ethereal Flow"],
            "wlan": ["Air Spirit", "Cloud Dancer", "Sky Whisper"],
            "wl": ["Air Spirit", "Cloud Dancer", "Sky Whisper"],
            "lo": ["Inner Echo", "Soul Mirror", "Self Reflection"],
            "veth": ["Bridge Guardian", "Gatekeeper", "Threshold Walker"],
            "docker": ["Container Spirit", "Boxed Essence", "Isolated Soul"],
            "podman": ["Container Spirit", "Boxed Essence", "Isolated Soul"],
            "tun": ["Tunnel Dreamer", "Veil Piercer", "Hidden Path"],
            "tap": ["Mirror Pool", "Reflection Well", "Surface Tension"],
            "virbr": ["Bridge Guardian", "Gatekeeper", "Threshold Walker"],
        }

        for prefix, spirit_names in names.items():
            if interface.startswith(prefix):
                return f"{random.choice(spirit_names)} ({interface})"

        mystic_suffixes = [
            " the Observer",
            " the Watcher",
            " the Listener",
            " the Silent",
            " the Flowing",
            " the Hidden",
        ]
        mystic_prefixes = [
            "Whispering ",
            "Echoing ",
            "Veiled ",
            "Ancient ",
            "Forgotten ",
            "Secret ",
        ]

        if random.random() > 0.5:
            return random.choice(mystic_prefixes) + interface
        return interface + random.choice(mystic_suffixes)

    def _generate_aura(self) -> str:
        auras = [
            "Pale Blue Mist",
            "Flickering Shadow",
            "Soft Golden Glow",
            "Deep Ocean Haze",
            "Forest Whisper Green",
            "Twilight Purple",
            "Dawn Orange",
            "Dusk Red",
            "Moon Silver",
            "Sun Gold",
        ]
        return random.choice(auras)

    def add_whisper(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.whispers.append(f"[{timestamp}] {message}")
        if len(self.whispers) > 5:
            self.whispers.pop(0)

    def update_counters(
        self,
        rx_bytes: int,
        tx_bytes: int,
        sample_time: float,
    ) -> None:
        elapsed = sample_time - self.last_sample_time
        if elapsed <= 0:
            return

        rx_delta = rx_bytes - self.rx_bytes
        tx_delta = tx_bytes - self.tx_bytes

        if rx_delta < 0 or tx_delta < 0:
            self.rx_rate = 0.0
            self.tx_rate = 0.0
        else:
            self.rx_rate = rx_delta / elapsed
            self.tx_rate = tx_delta / elapsed

        self.rx_bytes = rx_bytes
        self.tx_bytes = tx_bytes
        self.last_sample_time = sample_time
        self.last_seen = sample_time

    def update_glyphs(self, glyph_density: float) -> None:
        if len(self.glyphs) > 20:
            self.glyphs = self.glyphs[-20:]

        active_glyphs = []

        for glyph in self.glyphs:
            glyph.age += 1
            glyph.intensity *= 0.95

            if glyph.intensity > 0.1:
                active_glyphs.append(glyph)

            if glyph.type == GlyphType.FLOW:
                glyph.char = random.choice(
                    ["↗", "↘", "↖", "↙", "↕", "↔"]
                )
            elif glyph.type == GlyphType.PULSE:
                glyph.char = random.choice(
                    ["●", "○", "◎", "◉", "⊙"]
                )
            elif glyph.type == GlyphType.WHISPER:
                glyph.char = random.choice(
                    ["…", "~", "⋮", "⋯"]
                )
            elif glyph.type == GlyphType.SHADOW:
                glyph.char = random.choice(
                    ["░", "▒", "▓", "▚", "▞"]
                )
            elif glyph.type == GlyphType.ECHO:
                glyph.char = random.choice(
                    ["⦿", "⟳", "⟲", "↻", "↺"]
                )

        self.glyphs = active_glyphs

        traffic_rate = max(
            self.rx_rate + self.tx_rate,
            0.0,
        )

        flow_intensity = min(
            math.log1p(traffic_rate)
            / math.log1p(10_000_000),
            1.0,
        )

        density = max(
            0.0,
            min(glyph_density, 1.0),
        )

        if random.random() < flow_intensity * density:
            self.glyphs.append(
                Glyph(
                    type=GlyphType.FLOW,
                    intensity=max(
                        flow_intensity,
                        0.1,
                    ),
                    position=(
                        random.randint(0, 20),
                        random.randint(0, 5),
                    ),
                    color_pair=random.randint(1, 6),
                )
            )

        if random.random() < self.essence * density * 0.7:
            self.glyphs.append(
                Glyph(
                    type=GlyphType.WHISPER,
                    intensity=self.essence,
                    position=(
                        random.randint(0, 20),
                        random.randint(0, 5),
                    ),
                    color_pair=random.randint(1, 6),
                )
            )

        if random.random() < density * 0.08:
            glyph_type = random.choice(
                [
                    GlyphType.PULSE,
                    GlyphType.SHADOW,
                    GlyphType.ECHO,
                ]
            )

            self.glyphs.append(
                Glyph(
                    type=glyph_type,
                    intensity=random.uniform(
                        0.3,
                        1.0,
                    ),
                    position=(
                        random.randint(0, 20),
                        random.randint(0, 5),
                    ),
                    color_pair=random.randint(1, 6),
                )
            )


class MysticConfig:
    UPDATE_INTERVAL = 1.0
    GLYPH_DENSITY = 0.3
    MAX_SPIRITS = 20
    RITUAL_TIMEOUT = 30.0
    IP_CACHE_TTL = 10.0

    def __init__(self):
        self.update_interval = self.UPDATE_INTERVAL
        self.glyph_density = self.GLYPH_DENSITY
        self.show_whispers = True
        self.show_aura = True
        self.ancient_script = True
        self.log_file = "network_mysteries.jsonl"
        self.ritual_timeout = self.RITUAL_TIMEOUT
        self.max_spirits = self.MAX_SPIRITS
        self.show_loopback = False
        self.ip_cache_ttl = self.IP_CACHE_TTL

    def load_from_file(self, path: str) -> None:
        if not os.path.isfile(path):
            return

        try:
            with open(
                path,
                "r",
                encoding="utf-8",
            ) as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError):
            return

        validators = {
            "update_interval": self._positive_float,
            "glyph_density": self._density,
            "show_whispers": self._boolean,
            "show_aura": self._boolean,
            "ancient_script": self._boolean,
            "log_file": self._string,
            "ritual_timeout": self._positive_float,
            "max_spirits": self._positive_int,
            "show_loopback": self._boolean,
            "ip_cache_ttl": self._positive_float,
        }

        for key, validator in validators.items():
            if key not in data:
                continue

            try:
                setattr(
                    self,
                    key,
                    validator(data[key]),
                )
            except (TypeError, ValueError):
                continue

    @staticmethod
    def _positive_float(value) -> float:
        result = float(value)

        if result <= 0:
            raise ValueError

        return result

    @staticmethod
    def _positive_int(value) -> int:
        if isinstance(value, bool):
            raise ValueError

        result = int(value)

        if result <= 0:
            raise ValueError

        return result

    @staticmethod
    def _density(value) -> float:
        result = float(value)

        if not 0.0 <= result <= 1.0:
            raise ValueError

        return result

    @staticmethod
    def _boolean(value) -> bool:
        if not isinstance(value, bool):
            raise ValueError

        return value

    @staticmethod
    def _string(value) -> str:
        if not isinstance(value, str):
            raise ValueError

        return value


class AncientScript:
    @staticmethod
    def encode_number(num: float) -> str:
        symbols = [
            "Ⅰ",
            "Ⅱ",
            "Ⅲ",
            "Ⅳ",
            "Ⅴ",
            "Ⅵ",
            "Ⅶ",
            "Ⅷ",
            "Ⅸ",
            "Ⅹ",
            "Ⅺ",
            "Ⅻ",
            "ↀ",
            "ↁ",
            "ↂ",
            "Ↄ",
            "ↅ",
            "ↆ",
            "ↇ",
            "ↈ",
        ]

        if num < 1:
            return "↊"

        result = []
        int_part = int(num)

        while int_part > 0:
            symbol_idx = (
                int_part - 1
            ) % len(symbols)

            result.append(
                symbols[symbol_idx]
            )

            int_part //= len(symbols)

        return "".join(
            reversed(result)
        )

    @staticmethod
    def encode_rate(rate: float) -> str:
        rate = max(
            rate,
            0.0,
        )

        units = [
            "Ⓑ/ⓢ",
            "ⓀⒷ/ⓢ",
            "ⓂⒷ/ⓢ",
            "ⒼⒷ/ⓢ",
            "ⓉⒷ/ⓢ",
        ]

        divisors = [
            1,
            1024,
            1024**2,
            1024**3,
            1024**4,
        ]

        for i in range(
            len(units) - 1,
            -1,
            -1,
        ):
            if rate >= divisors[i]:
                value = rate / divisors[i]

                return (
                    f"{AncientScript.encode_number(value)} "
                    f"{units[i]}"
                )

        return f"↊ {units[0]}"

    @staticmethod
    def get_mystic_time() -> str:
        now = datetime.now()

        hour_symbols = [
            "子",
            "丑",
            "寅",
            "卯",
            "辰",
            "巳",
            "午",
            "未",
            "申",
            "酉",
            "戌",
            "亥",
        ]

        minute_symbols = [
            "初",
            "壹",
            "贰",
            "叁",
            "肆",
            "伍",
            "陆",
            "柒",
            "捌",
            "玖",
            "拾",
        ]

        hour_idx = now.hour % 12

        minute_idx = min(
            now.minute // 6,
            len(minute_symbols) - 1,
        )

        return (
            f"{hour_symbols[hour_idx]}"
            f"{minute_symbols[minute_idx]}刻"
        )


class WhisperCollector:
    def __init__(self):
        self.whispers = deque(
            maxlen=100
        )

    def add_whisper(
        self,
        source: str,
        message: str,
        level: str = "INFO",
    ) -> str:
        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        whisper = (
            f"[{timestamp}] "
            f"[{level}] "
            f"{source}: {message}"
        )

        self.whispers.append(
            whisper
        )

        return whisper

    def get_recent_whispers(
        self,
        count: int = 10,
    ) -> List[str]:
        return list(
            self.whispers
        )[-count:]


class NetworkMystic:
    def __init__(
        self,
        config: MysticConfig,
    ):
        self.config = config

        self.entities: Dict[
            str,
            NetworkEntity,
        ] = {}

        self.whispers = WhisperCollector()

        self.running = False

        self.colors: Dict[
            int,
            int,
        ] = {}

        self._lock = threading.Lock()
        self._cleanup_lock = threading.Lock()
        self._cleaned_up = False
        self._last_scan = 0.0
        self._last_ritual = 0.0

        self.rituals = [
            self._ritual_moon_cycle,
            self._ritual_tide_change,
            self._ritual_star_alignment,
            self._ritual_wind_shift,
        ]

    def init_colors(self) -> None:
        self.colors = {
            i: curses.A_NORMAL
            for i in range(1, 8)
        }

        if not curses.has_colors():
            return

        try:
            curses.start_color()
            curses.use_default_colors()

            color_pairs = [
                (
                    1,
                    curses.COLOR_BLUE,
                    -1,
                ),
                (
                    2,
                    curses.COLOR_CYAN,
                    -1,
                ),
                (
                    3,
                    curses.COLOR_GREEN,
                    -1,
                ),
                (
                    4,
                    curses.COLOR_MAGENTA,
                    -1,
                ),
                (
                    5,
                    curses.COLOR_YELLOW,
                    -1,
                ),
                (
                    6,
                    curses.COLOR_RED,
                    -1,
                ),
                (
                    7,
                    curses.COLOR_WHITE,
                    -1,
                ),
            ]

            for (
                pair_id,
                foreground,
                background,
            ) in color_pairs:
                curses.init_pair(
                    pair_id,
                    foreground,
                    background,
                )

                self.colors[
                    pair_id
                ] = curses.color_pair(
                    pair_id
                )

        except curses.error:
            self.colors = {
                i: curses.A_NORMAL
                for i in range(1, 8)
            }

    def _ritual_moon_cycle(self) -> str:
        moon_cycle = (
            time.time() % 2_419_200
        ) / 2_419_200

        if moon_cycle < 0.25:
            return (
                "New Moon: Spirits are quiet"
            )

        if moon_cycle < 0.5:
            return (
                "Waxing Moon: Connections strengthen"
            )

        if moon_cycle < 0.75:
            return (
                "Full Moon: Maximum flow"
            )

        return (
            "Waning Moon: Paths fade"
        )

    def _ritual_tide_change(self) -> str:
        tide = math.sin(
            time.time() / 3600
        )

        if tide > 0.7:
            return (
                "High Tide: Data flows freely"
            )

        if tide < -0.7:
            return (
                "Low Tide: Channels narrow"
            )

        return (
            "Changing Tide: Flux in patterns"
        )

    def _ritual_star_alignment(self) -> str:
        alignments = [
            "Stars favor communication",
            "Constellations whisper of packets",
            "Celestial paths clear",
            "Starlight reveals hidden flows",
            "Galactic currents shift",
        ]

        return random.choice(
            alignments
        )

    def _ritual_wind_shift(self) -> str:
        winds = [
            "Northern Wind: Cold data streams",
            "Southern Wind: Warm connections",
            "Eastern Wind: Dawn of new packets",
            "Western Wind: Dusk of old routes",
            "Still Air: Silent monitoring",
        ]

        return random.choice(
            winds
        )

    def perform_rituals(
        self,
        force: bool = False,
    ) -> None:
        now = time.monotonic()

        if (
            not force
            and now - self._last_ritual
            < self.config.ritual_timeout
        ):
            return

        ritual = random.choice(
            self.rituals
        )

        self.whispers.add_whisper(
            "Ritual",
            ritual(),
            "MYSTIC",
        )

        self._last_ritual = now

    def scan_spirits(self) -> None:
        try:
            with open(
                "/proc/net/dev",
                "r",
                encoding="utf-8",
            ) as handle:
                lines = handle.readlines()[2:]

        except OSError as exc:
            self.whispers.add_whisper(
                "Scanner",
                f"Failed to scan: {exc}",
                "ERROR",
            )
            return

        current_time = time.monotonic()
        found_interfaces = set()

        for line in lines:
            if (
                not line.strip()
                or ":" not in line
            ):
                continue

            (
                interface_part,
                data_part,
            ) = line.split(
                ":",
                1,
            )

            interface = (
                interface_part.strip()
            )

            if not interface:
                continue

            if (
                interface == "lo"
                and not self.config.show_loopback
            ):
                continue

            data = data_part.split()

            if len(data) < 16:
                continue

            try:
                rx_bytes = int(
                    data[0]
                )

                tx_bytes = int(
                    data[8]
                )

            except ValueError:
                continue

            found_interfaces.add(
                interface
            )

            if interface not in self.entities:
                entity = NetworkEntity(
                    interface,
                    rx_bytes,
                    tx_bytes,
                    current_time,
                )

                self.entities[
                    interface
                ] = entity

                self.whispers.add_whisper(
                    "Veil",
                    (
                        f"Spirit "
                        f"'{entity.name}' "
                        f"has appeared"
                    ),
                    "SPIRIT",
                )

            else:
                entity = self.entities[
                    interface
                ]

                entity.update_counters(
                    rx_bytes,
                    tx_bytes,
                    current_time,
                )

            self._refresh_entity_ips(
                entity,
                current_time,
            )

            self._update_entity_whispers(
                entity
            )

            entity.update_glyphs(
                self.config.glyph_density
            )

        expired = [
            interface
            for interface in self.entities
            if interface
            not in found_interfaces
        ]

        for interface in expired:
            spirit = self.entities.pop(
                interface
            )

            self.whispers.add_whisper(
                "Veil",
                (
                    f"Spirit "
                    f"'{spirit.name}' "
                    f"has faded"
                ),
                "SPIRIT",
            )

        self._last_scan = current_time

    def _update_entity_whispers(
        self,
        entity: NetworkEntity,
    ) -> None:
        if entity.rx_rate > 1_000_000:
            entity.add_whisper(
                "Great flow from beyond"
            )

        elif (
            entity.rx_rate < 1_000
            and entity.tx_rate < 1_000
        ):
            entity.add_whisper(
                "Resting in silence"
            )

        elif (
            entity.rx_rate
            > entity.tx_rate * 2
        ):
            entity.add_whisper(
                "Listening more than speaking"
            )

        elif (
            entity.tx_rate
            > entity.rx_rate * 2
        ):
            entity.add_whisper(
                "Whispering to the void"
            )

    def _refresh_entity_ips(
        self,
        entity: NetworkEntity,
        current_time: float,
    ) -> None:
        if (
            current_time
            - entity.last_ip_refresh
            < self.config.ip_cache_ttl
        ):
            return

        entity.ips = (
            self.get_interface_ips(
                entity.interface
            )
        )

        entity.last_ip_refresh = (
            current_time
        )

    def get_interface_ips(
        self,
        interface: str,
    ) -> List[str]:
        try:
            result = subprocess.run(
                [
                    "ip",
                    "-o",
                    "-4",
                    "addr",
                    "show",
                    "dev",
                    interface,
                ],
                capture_output=True,
                text=True,
                timeout=2,
                check=False,
            )

        except (
            OSError,
            subprocess.TimeoutExpired,
        ):
            return []

        ips = []

        for line in result.stdout.splitlines():
            parts = line.split()

            if len(parts) >= 4:
                ip = (
                    parts[3]
                    .split("/", 1)[0]
                )

                if (
                    ip
                    and ip != "127.0.0.1"
                ):
                    ips.append(ip)

        return ips

    @staticmethod
    def _safe_addstr(
        screen,
        y: int,
        x: int,
        text: str,
        attr: int = curses.A_NORMAL,
    ) -> None:
        height, width = (
            screen.getmaxyx()
        )

        if (
            y < 0
            or y >= height
            or x < 0
            or x >= width
        ):
            return

        available = width - x

        if available <= 0:
            return

        try:
            screen.addnstr(
                y,
                x,
                text,
                available,
                attr,
            )
        except curses.error:
            return

    def draw_veil_border(
        self,
        screen,
        height: int,
        width: int,
    ) -> None:
        if (
            width < 2
            or height < 2
        ):
            return

        top = (
            "╔"
            + "═"
            * max(
                width - 2,
                0,
            )
            + "╗"
        )

        bottom = (
            "╚"
            + "═"
            * max(
                width - 2,
                0,
            )
            + "╝"
        )

        self._safe_addstr(
            screen,
            0,
            0,
            top,
        )

        self._safe_addstr(
            screen,
            height - 1,
            0,
            bottom,
        )

        for y in range(
            1,
            height - 1,
        ):
            self._safe_addstr(
                screen,
                y,
                0,
                "║",
            )

            self._safe_addstr(
                screen,
                y,
                width - 1,
                "║",
            )

    def render_glyph(
        self,
        screen,
        glyph: Glyph,
        offset_x: int,
        offset_y: int,
    ) -> None:
        x, y = glyph.position

        screen_x = (
            offset_x + x
        )

        screen_y = (
            offset_y + y
        )

        attr = self.colors.get(
            glyph.color_pair,
            curses.A_NORMAL,
        )

        if glyph.intensity > 0.6:
            attr |= curses.A_BOLD

        elif glyph.intensity < 0.3:
            attr |= curses.A_DIM

        self._safe_addstr(
            screen,
            screen_y,
            screen_x,
            glyph.char,
            attr,
        )

    def render_flow_visualization(
        self,
        screen,
        rx_rate: float,
        tx_rate: float,
        x: int,
        y: int,
        width: int,
    ) -> None:
        if width < 3:
            return

        rx_height = (
            self._rate_to_height(
                rx_rate,
                5,
            )
        )

        tx_height = (
            self._rate_to_height(
                tx_rate,
                5,
            )
        )

        bars = "▁▂▃▄▅▆▇█"

        for index in range(
            rx_height
        ):
            char_idx = min(
                index
                * len(bars)
                // 5,
                len(bars) - 1,
            )

            self._safe_addstr(
                screen,
                y + 4 - index,
                x,
                bars[char_idx],
                self.colors.get(
                    2,
                    curses.A_NORMAL,
                ),
            )

        for index in range(
            tx_height
        ):
            char_idx = min(
                index
                * len(bars)
                // 5,
                len(bars) - 1,
            )

            self._safe_addstr(
                screen,
                y + 4 - index,
                x + 2,
                bars[char_idx],
                self.colors.get(
                    3,
                    curses.A_NORMAL,
                ),
            )

    @staticmethod
    def _rate_to_height(
        rate: float,
        height: int,
    ) -> int:
        if rate <= 0:
            return 0

        normalized = (
            math.log1p(rate)
            / math.log1p(
                10_000_000
            )
        )

        return max(
            1,
            min(
                int(
                    math.ceil(
                        normalized
                        * height
                    )
                ),
                height,
            ),
        )

    def draw_spirit_info(
        self,
        screen,
        entity: NetworkEntity,
        y_start: int,
    ) -> None:
        height, width = (
            screen.getmaxyx()
        )

        if (
            y_start >= height - 2
            or width < 20
        ):
            return

        ip_display = (
            ", ".join(entity.ips)
            if entity.ips
            else "[No physical form]"
        )

        self._safe_addstr(
            screen,
            y_start,
            2,
            f"╭─ {entity.name}",
            curses.A_BOLD,
        )

        line = 1

        if self.config.show_aura:
            self._safe_addstr(
                screen,
                y_start + line,
                2,
                f"│  Aura: {entity.aura}",
                self.colors.get(
                    4,
                    curses.A_NORMAL,
                ),
            )

            line += 1

        if self.config.ancient_script:
            rx_display = (
                AncientScript.encode_rate(
                    entity.rx_rate
                )
            )

            tx_display = (
                AncientScript.encode_rate(
                    entity.tx_rate
                )
            )

        else:
            rx_display = (
                self.format_rate(
                    entity.rx_rate
                )
            )

            tx_display = (
                self.format_rate(
                    entity.tx_rate
                )
            )

        self._safe_addstr(
            screen,
            y_start + line,
            2,
            (
                f"│  From Beyond: "
                f"{rx_display}"
            ),
            self.colors.get(
                2,
                curses.A_NORMAL,
            ),
        )

        line += 1

        self._safe_addstr(
            screen,
            y_start + line,
            2,
            (
                f"│  To Void:     "
                f"{tx_display}"
            ),
            self.colors.get(
                3,
                curses.A_NORMAL,
            ),
        )

        line += 1

        self._safe_addstr(
            screen,
            y_start + line,
            2,
            (
                f"│  Essence: "
                f"{entity.essence:.2f}"
            ),
            curses.A_DIM,
        )

        line += 1

        self._safe_addstr(
            screen,
            y_start + line,
            2,
            f"│  Form: {ip_display}",
            curses.A_DIM,
        )

        line += 1

        if width >= 48:
            self.render_flow_visualization(
                screen,
                entity.rx_rate,
                entity.tx_rate,
                40,
                y_start + 1,
                width - 40,
            )

        for whisper in (
            entity.whispers[-2:]
        ):
            if (
                y_start + line
                >= height - 2
            ):
                break

            self._safe_addstr(
                screen,
                y_start + line,
                2,
                f"│  {whisper}",
                curses.A_DIM,
            )

            line += 1

        if (
            y_start + line
            < height - 1
        ):
            border_width = max(
                width - 4,
                1,
            )

            self._safe_addstr(
                screen,
                y_start + line,
                2,
                (
                    "╰"
                    + "─"
                    * max(
                        border_width - 1,
                        0,
                    )
                ),
            )

        for glyph in entity.glyphs:
            self.render_glyph(
                screen,
                glyph,
                25,
                y_start - 4,
            )

    @staticmethod
    def format_rate(
        rate: float,
    ) -> str:
        rate = max(
            rate,
            0.0,
        )

        units = [
            "B/s",
            "KB/s",
            "MB/s",
            "GB/s",
            "TB/s",
        ]

        for unit in units:
            if (
                rate < 1024.0
                or unit == units[-1]
            ):
                return (
                    f"{rate:.1f} "
                    f"{unit}"
                )

            rate /= 1024.0

        return "0.0 B/s"

    def draw_veil(
        self,
        screen,
    ) -> None:
        screen.erase()

        height, width = (
            screen.getmaxyx()
        )

        if (
            height < 8
            or width < 30
        ):
            message = (
                "Terminal too small"
            )

            self._safe_addstr(
                screen,
                max(
                    height // 2,
                    0,
                ),
                max(
                    (
                        width
                        - len(message)
                    )
                    // 2,
                    0,
                ),
                message,
                curses.A_BOLD,
            )

            try:
                screen.refresh()
            except curses.error:
                pass

            return

        self.draw_veil_border(
            screen,
            height,
            width,
        )

        title = (
            "╡ Network Mystic ╞"
        )

        title_x = max(
            1,
            (
                width
                - len(title)
            )
            // 2,
        )

        self._safe_addstr(
            screen,
            0,
            title_x,
            title,
            (
                curses.A_BOLD
                | self.colors.get(
                    1,
                    curses.A_NORMAL,
                )
            ),
        )

        mystic_time = (
            AncientScript.get_mystic_time()
        )

        time_x = (
            width
            - len(mystic_time)
            - 2
        )

        if (
            time_x
            > title_x + len(title)
        ):
            self._safe_addstr(
                screen,
                0,
                time_x,
                mystic_time,
                curses.A_DIM,
            )

        spirits = sorted(
            self.entities.values(),
            key=lambda entity: (
                entity.rx_rate
                + entity.tx_rate
            ),
            reverse=True,
        )

        y = 2
        reserved_bottom = 4

        for spirit in spirits[
            : self.config.max_spirits
        ]:
            block_height = (
                9
                if self.config.show_aura
                else 8
            )

            if (
                y + block_height
                >= height
                - reserved_bottom
            ):
                break

            self.draw_spirit_info(
                screen,
                spirit,
                y,
            )

            y += block_height

        self.draw_whispers_panel(
            screen,
            height,
            width,
        )

        self.draw_status_bar(
            screen,
            height,
            width,
        )

        try:
            screen.refresh()
        except curses.error:
            pass

    def draw_status_bar(
        self,
        screen,
        height: int,
        width: int,
    ) -> None:
        if (
            height < 4
            or width < 8
        ):
            return

        total_rx = sum(
            entity.rx_rate
            for entity
            in self.entities.values()
        )

        total_tx = sum(
            entity.tx_rate
            for entity
            in self.entities.values()
        )

        if self.config.ancient_script:
            total_rx_display = (
                AncientScript.encode_rate(
                    total_rx
                )
            )

            total_tx_display = (
                AncientScript.encode_rate(
                    total_tx
                )
            )

        else:
            total_rx_display = (
                self.format_rate(
                    total_rx
                )
            )

            total_tx_display = (
                self.format_rate(
                    total_tx
                )
            )

        status = (
            f"Total Flow: "
            f"{total_rx_display} "
            f"╫ "
            f"{total_tx_display}"
        )

        status += (
            f" │ Spirits: "
            f"{len(self.entities)}"
        )

        status += (
            f" │ "
            f"{AncientScript.get_mystic_time()}"
        )

        max_length = max(
            width - 4,
            0,
        )

        status = status[
            :max_length
        ]

        status_x = max(
            1,
            (
                width
                - len(status)
            )
            // 2,
        )

        self._safe_addstr(
            screen,
            height - 3,
            status_x,
            status,
            curses.A_DIM,
        )

    def draw_whispers_panel(
        self,
        screen,
        height: int,
        width: int,
    ) -> None:
        if (
            not self.config.show_whispers
            or height < 8
            or width < 60
        ):
            return

        panel_width = min(
            50,
            max(
                width // 3,
                24,
            ),
        )

        panel_x = (
            width
            - panel_width
            - 2
        )

        if panel_x < 2:
            return

        self._safe_addstr(
            screen,
            1,
            panel_x,
            "╭─[Whispers]─",
            curses.A_DIM,
        )

        whispers = (
            self.whispers
            .get_recent_whispers(
                min(
                    8,
                    height - 5,
                )
            )
        )

        for (
            index,
            whisper,
        ) in enumerate(whispers):
            line = whisper[
                : max(
                    panel_width - 2,
                    0,
                )
            ]

            self._safe_addstr(
                screen,
                2 + index,
                panel_x,
                f"│{line}",
                curses.A_DIM,
            )

        side_x = (
            panel_x
            + panel_width
        )

        for y in range(
            1,
            min(
                len(whispers) + 2,
                height - 2,
            ),
        ):
            self._safe_addstr(
                screen,
                y,
                side_x,
                "│",
                curses.A_DIM,
            )

        end_y = min(
            len(whispers) + 2,
            height - 2,
        )

        self._safe_addstr(
            screen,
            end_y,
            panel_x,
            (
                "╰"
                + "─"
                * panel_width
            ),
            curses.A_DIM,
        )

    def force_refresh(
        self,
        screen,
    ) -> None:
        self.scan_spirits()
        self.perform_rituals()
        self.draw_veil(screen)

        self.whispers.add_whisper(
            "Mystic",
            "Ritual refreshed",
            "INFO",
        )

    def run_ritual(
        self,
        screen,
    ) -> None:
        self.init_colors()

        try:
            curses.curs_set(0)
        except curses.error:
            pass

        screen.nodelay(True)
        screen.timeout(100)

        self.running = True

        self.whispers.add_whisper(
            "Mystic",
            "Beginning the ritual...",
            "INFO",
        )

        self.scan_spirits()
        self.draw_veil(screen)

        while self.running:
            try:
                key = screen.getch()

                if key == ord("q"):
                    self.stop()

                elif key == ord(" "):
                    self.perform_rituals(
                        force=True
                    )

                    self.draw_veil(
                        screen
                    )

                elif key == ord("r"):
                    self.force_refresh(
                        screen
                    )

                elif key == ord("l"):
                    self.config.show_loopback = (
                        not self.config.show_loopback
                    )

                    status = (
                        "shown"
                        if self.config.show_loopback
                        else "hidden"
                    )

                    self.whispers.add_whisper(
                        "Mystic",
                        (
                            f"Loopback spirits "
                            f"{status}"
                        ),
                        "INFO",
                    )

                    self.scan_spirits()
                    self.draw_veil(
                        screen
                    )

                elif key == ord("a"):
                    self.config.ancient_script = (
                        not self.config.ancient_script
                    )

                    status = (
                        "enabled"
                        if self.config.ancient_script
                        else "disabled"
                    )

                    self.whispers.add_whisper(
                        "Mystic",
                        (
                            f"Ancient script "
                            f"{status}"
                        ),
                        "INFO",
                    )

                    self.draw_veil(
                        screen
                    )

                elif key == ord("w"):
                    self.config.show_whispers = (
                        not self.config.show_whispers
                    )

                    status = (
                        "enabled"
                        if self.config.show_whispers
                        else "disabled"
                    )

                    self.whispers.add_whisper(
                        "Mystic",
                        (
                            f"Whispers "
                            f"{status}"
                        ),
                        "INFO",
                    )

                    self.draw_veil(
                        screen
                    )

                now = time.monotonic()

                if (
                    now
                    - self._last_scan
                    >= self.config.update_interval
                ):
                    self.scan_spirits()
                    self.perform_rituals()
                    self.draw_veil(
                        screen
                    )

                time.sleep(0.01)

            except KeyboardInterrupt:
                self.stop()

            except curses.error:
                continue

            except Exception as exc:
                self.whispers.add_whisper(
                    "Mystic",
                    f"Error: {exc}",
                    "ERROR",
                )

                time.sleep(0.1)

    def save_mysteries(
        self,
    ) -> None:
        if not self.config.log_file:
            return

        mysteries = []

        for entity in (
            self.entities.values()
        ):
            mysteries.append(
                {
                    "spirit": entity.name,
                    "interface": entity.interface,
                    "essence": entity.essence,
                    "aura": entity.aura,
                    "total_rx": entity.rx_bytes,
                    "total_tx": entity.tx_bytes,
                    "rx_rate": entity.rx_rate,
                    "tx_rate": entity.tx_rate,
                    "ips": entity.ips,
                    "whispers": entity.whispers[-5:],
                    "timestamp": datetime.now().isoformat(),
                }
            )

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "mystic_time": AncientScript.get_mystic_time(),
            "total_spirits": len(self.entities),
            "mysteries": mysteries,
            "system_whispers": self.whispers.get_recent_whispers(10),
        }

        try:
            with open(
                self.config.log_file,
                "a",
                encoding="utf-8",
            ) as handle:
                handle.write(
                    json.dumps(
                        log_entry,
                        ensure_ascii=False,
                        separators=(
                            ",",
                            ":",
                        ),
                    )
                )

                handle.write("\n")

        except OSError as exc:
            self.whispers.add_whisper(
                "Archivist",
                f"Failed to save: {exc}",
                "ERROR",
            )

    def start(self) -> None:
        curses.wrapper(
            self.run_ritual
        )

    def cleanup(self) -> None:
        with self._cleanup_lock:
            if self._cleaned_up:
                return

            self._cleaned_up = True

        self.whispers.add_whisper(
            "Mystic",
            (
                "Ritual complete. "
                "Veil closing..."
            ),
            "INFO",
        )

        self.save_mysteries()

        if self.config.log_file:
            sys.stderr.write(
                (
                    "\nMysteries saved to "
                    f"{self.config.log_file}\n"
                )
            )

        sys.stderr.write(
            "\nMay the flows guide you...\n"
        )

        sys.stderr.write(
            "\nControls:\n"
        )

        sys.stderr.write(
            "  q - Quit\n"
        )

        sys.stderr.write(
            "  Space - Perform ritual\n"
        )

        sys.stderr.write(
            "  r - Refresh\n"
        )

        sys.stderr.write(
            (
                "  l - Toggle "
                "loopback spirits\n"
            )
        )

        sys.stderr.write(
            (
                "  a - Toggle "
                "ancient script\n"
            )
        )

        sys.stderr.write(
            (
                "  w - Toggle "
                "whispers\n"
            )
        )

    def stop(self) -> None:
        with self._lock:
            self.running = False


def main() -> None:
    config = MysticConfig()

    if len(sys.argv) > 1:
        config.load_from_file(
            sys.argv[1]
        )

    mystic = NetworkMystic(
        config
    )

    atexit.register(
        mystic.cleanup
    )

    signal.signal(
        signal.SIGINT,
        lambda _signal_number, _frame: mystic.stop(),
    )

    signal.signal(
        signal.SIGTERM,
        lambda _signal_number, _frame: mystic.stop(),
    )

    try:
        mystic.start()
    finally:
        mystic.cleanup()


if __name__ == "__main__":
    main()
