#!/usr/bin/env python3

import os
import sys
import time
import signal
import subprocess
import random
import json
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from collections import deque, defaultdict
import curses
import curses.textpad
import atexit

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
    def __init__(self, name: str, interface: str):
        self.name = self._generate_spirit_name(name)
        self.interface = interface
        self.rx_bytes = 0
        self.tx_bytes = 0
        self.rx_rate = 0.0
        self.tx_rate = 0.0
        self.essence = random.uniform(0.1, 1.0)
        self.aura = self._generate_aura()
        self.glyphs: List[Glyph] = []
        self.last_seen = time.time()
        self.whispers: List[str] = []
        
    def _generate_spirit_name(self, interface: str) -> str:
        names = {
            'eth': ['Silent River', 'Whispering Wind', 'Ethereal Flow'],
            'wlan': ['Air Spirit', 'Cloud Dancer', 'Sky Whisper'],
            'lo': ['Inner Echo', 'Soul Mirror', 'Self Reflection'],
            'veth': ['Bridge Guardian', 'Gatekeeper', 'Threshold Walker'],
            'docker': ['Container Spirit', 'Boxed Essence', 'Isolated Soul'],
            'tun': ['Tunnel Dreamer', 'Veil Piercer', 'Hidden Path'],
            'tap': ['Mirror Pool', 'Reflection Well', 'Surface Tension']
        }
        
        for prefix, spirit_names in names.items():
            if interface.startswith(prefix):
                return f"{random.choice(spirit_names)} ({interface})"
        
        mystic_suffixes = [' the Observer', ' the Watcher', ' the Listener', 
                          ' the Silent', ' the Flowing', ' the Hidden']
        mystic_prefixes = ['Whispering ', 'Echoing ', 'Veiled ', 'Ancient ', 
                          'Forgotten ', 'Secret ']
        
        if random.random() > 0.5:
            name = random.choice(mystic_prefixes) + interface
        else:
            name = interface + random.choice(mystic_suffixes)
            
        return name
    
    def _generate_aura(self) -> str:
        auras = [
            "Pale Blue Mist", "Flickering Shadow", "Soft Golden Glow",
            "Deep Ocean Haze", "Forest Whisper Green", "Twilight Purple",
            "Dawn Orange", "Dusk Red", "Moon Silver", "Sun Gold"
        ]
        return random.choice(auras)
    
    def add_whisper(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.whispers.append(f"[{timestamp}] {message}")
        if len(self.whispers) > 5:
            self.whispers.pop(0)
    
    def update_glyphs(self):
        active_glyphs = []
        for glyph in self.glyphs:
            glyph.age += 1
            glyph.intensity *= 0.95
            
            if glyph.intensity > 0.1:
                active_glyphs.append(glyph)
                
            if glyph.type == GlyphType.FLOW:
                glyph.char = random.choice(["↗", "↘", "↖", "↙", "↕", "↔"])
            elif glyph.type == GlyphType.PULSE:
                glyph.char = random.choice(["●", "○", "◎", "◉", "⊙"])
            elif glyph.type == GlyphType.WHISPER:
                glyph.char = random.choice(["…", "~", "⋮", "⋯"])
            elif glyph.type == GlyphType.SHADOW:
                glyph.char = random.choice(["░", "▒", "▓", "▚", "▞"])
            elif glyph.type == GlyphType.ECHO:
                glyph.char = random.choice(["⦿", "⟳", "⟲", "↻", "↺"])
        
        self.glyphs = active_glyphs
        
        flow_intensity = min(self.rx_rate + self.tx_rate, 1000) / 1000
        
        if random.random() < flow_intensity * 0.3:
            x = random.randint(0, 20)
            y = random.randint(0, 5)
            self.glyphs.append(Glyph(
                type=GlyphType.FLOW,
                intensity=flow_intensity,
                position=(x, y),
                color_pair=random.randint(1, 6)
            ))
        
        if random.random() < self.essence * 0.2:
            x = random.randint(0, 20)
            y = random.randint(0, 5)
            self.glyphs.append(Glyph(
                type=GlyphType.WHISPER,
                intensity=self.essence,
                position=(x, y),
                color_pair=random.randint(1, 6)
            ))

class MysticConfig:
    def __init__(self):
        self.update_interval = 1.0
        self.glyph_density = 0.3
        self.show_whispers = True
        self.show_aura = True
        self.ancient_script = True
        self.encrypt_logs = False
        self.log_file = "network_mysteries.log"
        self.ritual_timeout = 30
        self.max_spirits = 20
        self.show_loopback = False
        
    def load_from_file(self, path: str):
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                for key, value in data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
        except FileNotFoundError:
            pass

class AncientScript:
    @staticmethod
    def encode_number(num: float) -> str:
        symbols = ["Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ", "Ⅵ", "Ⅶ", "Ⅷ", "Ⅸ", "Ⅹ",
                  "Ⅺ", "Ⅻ", "ↀ", "ↁ", "ↂ", "Ↄ", "ↅ", "ↆ", "ↇ", "ↈ"]
        
        if num < 1:
            return "↊"
        
        result = []
        int_part = int(num)
        
        while int_part > 0:
            symbol_idx = (int_part - 1) % len(symbols)
            result.append(symbols[symbol_idx])
            int_part //= len(symbols)
        
        return "".join(reversed(result))
    
    @staticmethod
    def encode_rate(rate: float) -> str:
        units = ["Ⓑ/ⓢ", "ⓀⒷ/ⓢ", "ⓂⒷ/ⓢ", "ⒼⒷ/ⓢ", "ⓉⒷ/ⓢ"]
        divisors = [1, 1024, 1024**2, 1024**3, 1024**4]
        
        for i in range(len(units) - 1, -1, -1):
            if rate >= divisors[i]:
                value = rate / divisors[i]
                symbol = AncientScript.encode_number(value)
                return f"{symbol} {units[i]}"
        
        return f"↊ {units[0]}"
    
    @staticmethod
    def get_mystic_time() -> str:
        now = datetime.now()
        hour_symbols = ["子", "丑", "寅", "卯", "辰", "巳", 
                       "午", "未", "申", "酉", "戌", "亥"]
        minute_symbols = ["初", "壹", "贰", "叁", "肆", "伍", 
                         "陆", "柒", "捌", "玖", "拾"]
        
        hour_idx = now.hour % 12
        minute_idx = now.minute // 6
        
        return f"{hour_symbols[hour_idx]}{minute_symbols[minute_idx]}刻"

class WhisperCollector:
    def __init__(self):
        self.whispers = deque(maxlen=100)
        
    def add_whisper(self, source: str, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        whisper = f"[{timestamp}] [{level}] {source}: {message}"
        self.whispers.append(whisper)
        return whisper
    
    def get_recent_whispers(self, count: int = 10) -> List[str]:
        return list(self.whispers)[-count:]

class NetworkMystic:
    def __init__(self, config: MysticConfig):
        self.config = config
        self.entities: Dict[str, NetworkEntity] = {}
        self.whispers = WhisperCollector()
        self.last_update = time.time()
        self.running = False
        self.colors = {}
        self.init_rituals()
        
    def init_rituals(self):
        self.rituals = [
            self._ritual_moon_cycle,
            self._ritual_tide_change,
            self._ritual_star_alignment,
            self._ritual_wind_shift
        ]
    
    def init_colors(self):
        curses.start_color()
        curses.use_default_colors()
        
        color_pairs = [
            (1, curses.COLOR_BLUE, curses.COLOR_BLACK),
            (2, curses.COLOR_CYAN, curses.COLOR_BLACK),
            (3, curses.COLOR_GREEN, curses.COLOR_BLACK),
            (4, curses.COLOR_MAGENTA, curses.COLOR_BLACK),
            (5, curses.COLOR_YELLOW, curses.COLOR_BLACK),
            (6, curses.COLOR_RED, curses.COLOR_BLACK),
            (7, curses.COLOR_WHITE, curses.COLOR_BLACK),
        ]
        
        for pair_id, fg, bg in color_pairs:
            curses.init_pair(pair_id, fg, bg)
            self.colors[pair_id] = curses.color_pair(pair_id)
    
    def _ritual_moon_cycle(self):
        now = time.time()
        moon_cycle = (now % 2419200) / 2419200
        
        if moon_cycle < 0.25:
            return "New Moon: Spirits are quiet"
        elif moon_cycle < 0.5:
            return "Waxing Moon: Connections strengthen"
        elif moon_cycle < 0.75:
            return "Full Moon: Maximum flow"
        else:
            return "Waning Moon: Paths fade"
    
    def _ritual_tide_change(self):
        tide = math.sin(time.time() / 3600)
        
        if tide > 0.7:
            return "High Tide: Data flows freely"
        elif tide < -0.7:
            return "Low Tide: Channels narrow"
        else:
            return "Changing Tide: Flux in patterns"
    
    def _ritual_star_alignment(self):
        alignments = [
            "Stars favor communication",
            "Constellations whisper of packets",
            "Celestial paths clear",
            "Starlight reveals hidden flows",
            "Galactic currents shift"
        ]
        return random.choice(alignments)
    
    def _ritual_wind_shift(self):
        winds = [
            "Northern Wind: Cold data streams",
            "Southern Wind: Warm connections",
            "Eastern Wind: Dawn of new packets",
            "Western Wind: Dusk of old routes",
            "Still Air: Silent monitoring"
        ]
        return random.choice(winds)
    
    def perform_rituals(self):
        if random.random() < 0.1:
            ritual = random.choice(self.rituals)
            result = ritual()
            self.whispers.add_whisper("Ritual", result, "MYSTIC")
    
    def scan_spirits(self):
        try:
            with open('/proc/net/dev', 'r') as f:
                lines = f.readlines()[2:]
            
            current_time = time.time()
            found_interfaces = set()
            
            for line in lines:
                if not line.strip():
                    continue
                    
                parts = line.split(':')
                if len(parts) < 2:
                    continue
                    
                interface = parts[0].strip()
                if not interface or (interface == 'lo' and not self.config.show_loopback):
                    continue
                
                found_interfaces.add(interface)
                
                data = parts[1].split()
                if len(data) < 16:
                    continue
                
                rx_bytes = int(data[0])
                tx_bytes = int(data[8])
                
                if interface not in self.entities:
                    spirit = NetworkEntity(interface, interface)
                    self.entities[interface] = spirit
                    self.whispers.add_whisper("Veil", 
                        f"Spirit '{spirit.name}' has appeared", "SPIRIT")
                
                entity = self.entities[interface]
                entity.last_seen = current_time
                
                time_diff = current_time - self.last_update
                if time_diff > 0:
                    entity.rx_rate = (rx_bytes - entity.rx_bytes) / time_diff
                    entity.tx_rate = (tx_bytes - entity.tx_bytes) / time_diff
                
                entity.rx_bytes = rx_bytes
                entity.tx_bytes = tx_bytes
                
                if entity.rx_rate > 1000000:
                    entity.add_whisper("Great flow from beyond")
                elif entity.rx_rate < 1000 and entity.tx_rate < 1000:
                    entity.add_whisper("Resting in silence")
                elif entity.rx_rate > entity.tx_rate * 2:
                    entity.add_whisper("Listening more than speaking")
                elif entity.tx_rate > entity.rx_rate * 2:
                    entity.add_whisper("Whispering to the void")
                
                entity.update_glyphs()
            
            expired = []
            for iface, entity in self.entities.items():
                if iface not in found_interfaces:
                    expired.append(iface)
            
            for iface in expired:
                spirit = self.entities.pop(iface)
                self.whispers.add_whisper("Veil",
                    f"Spirit '{spirit.name}' has faded", "SPIRIT")
                
        except Exception as e:
            self.whispers.add_whisper("Scanner", f"Failed to scan: {str(e)}", "ERROR")
    
    def get_interface_ips(self, interface: str) -> List[str]:
        try:
            result = subprocess.run(['ip', '-o', '-4', 'addr', 'show', interface],
                                  capture_output=True, text=True, timeout=2)
            ips = []
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 4:
                    ip = parts[3].split('/')[0]
                    if ip and ip != '127.0.0.1':
                        ips.append(ip)
            return ips
        except:
            return []
    
    def draw_veil_border(self, screen, height, width):
        border_chars = ["╔", "╗", "╚", "╝", "═", "║"]
        
        for y in range(height):
            if y == 0:
                try:
                    screen.addstr(y, 0, border_chars[0] + border_chars[4] * (width - 2) + border_chars[1])
                except:
                    pass
            elif y == height - 1:
                try:
                    screen.addstr(y, 0, border_chars[2] + border_chars[4] * (width - 2) + border_chars[3])
                except:
                    pass
            else:
                try:
                    screen.addstr(y, 0, border_chars[5])
                    screen.addstr(y, width - 1, border_chars[5])
                except:
                    pass
    
    def render_glyph(self, screen, glyph: Glyph, offset_x: int, offset_y: int):
        x, y = glyph.position
        screen_x = offset_x + x
        screen_y = offset_y + y
        
        if 0 <= screen_x < curses.COLS and 0 <= screen_y < curses.LINES:
            try:
                attr = self.colors.get(glyph.color_pair, curses.A_NORMAL)
                if glyph.intensity > 0.3:
                    attr |= curses.A_BOLD
                if glyph.intensity < 0.6:
                    attr |= curses.A_DIM
                    
                screen.addstr(screen_y, screen_x, glyph.char, attr)
            except:
                pass
    
    def render_flow_visualization(self, screen, rx_rate: float, tx_rate: float, x: int, y: int, width: int):
        max_rate = 1000
        rx_height = min(int((rx_rate / max_rate) * 5), 5)
        tx_height = min(int((tx_rate / max_rate) * 5), 5)
        
        rx_bar = "▁▂▃▄▅▆▇█"
        tx_bar = "▁▂▃▄▅▆▇█"
        
        for i in range(rx_height):
            char_idx = min(i * len(rx_bar) // 5, len(rx_bar) - 1)
            try:
                screen.addstr(y + 4 - i, x, rx_bar[char_idx], self.colors[2])
            except:
                pass
        
        for i in range(tx_height):
            char_idx = min(i * len(tx_bar) // 5, len(tx_bar) - 1)
            try:
                screen.addstr(y + 4 - i, x + 2, tx_bar[char_idx], self.colors[3])
            except:
                pass
    
    def draw_spirit_info(self, screen, entity: NetworkEntity, y_start: int):
        try:
            ips = self.get_interface_ips(entity.interface)
            ip_display = ", ".join(ips) if ips else "[No physical form]"
            
            screen.addstr(y_start, 2, f"╭─ {entity.name}", curses.A_BOLD)
            screen.addstr(y_start + 1, 2, f"│  Aura: {entity.aura}", self.colors[4])
            
            if self.config.ancient_script:
                rx_display = AncientScript.encode_rate(entity.rx_rate)
                tx_display = AncientScript.encode_rate(entity.tx_rate)
            else:
                rx_display = self.format_rate(entity.rx_rate)
                tx_display = self.format_rate(entity.tx_rate)
            
            screen.addstr(y_start + 2, 2, f"│  From Beyond: {rx_display}", 
                         self.colors[2])
            screen.addstr(y_start + 3, 2, f"│  To Void:     {tx_display}", 
                         self.colors[3])
            screen.addstr(y_start + 4, 2, f"│  Essence: {entity.essence:.2f}", 
                         curses.A_DIM)
            screen.addstr(y_start + 5, 2, f"│  Form: {ip_display}", curses.A_DIM)
            
            self.render_flow_visualization(screen, entity.rx_rate, entity.tx_rate, 40, y_start + 1, 10)
            
            whisper_y = y_start + 6
            for whisper in entity.whispers[-2:]:
                if whisper_y < curses.LINES - 2:
                    try:
                        screen.addstr(whisper_y, 2, f"│  {whisper}", curses.A_DIM)
                        whisper_y += 1
                    except:
                        pass
            
            try:
                screen.addstr(whisper_y, 2, "╰" + "─" * (curses.COLS - 4))
            except:
                pass
            
            for glyph in entity.glyphs:
                self.render_glyph(screen, glyph, 25, y_start - 4)
                
        except curses.error:
            pass
    
    def format_rate(self, rate: float) -> str:
        units = ['B/s', 'KB/s', 'MB/s', 'GB/s', 'TB/s']
        divisor = 1024.0
        
        for unit in units:
            if rate < divisor or unit == units[-1]:
                return f"{rate:.1f} {unit}"
            rate /= divisor
        return "0 B/s"
    
    def draw_veil(self, screen):
        try:
            screen.clear()
            height, width = screen.getmaxyx()
            
            self.draw_veil_border(screen, height, width)
            
            title = "╡ Network Mystic ╞"
            title_x = max(0, (width - len(title)) // 2)
            try:
                screen.addstr(0, title_x, title, curses.A_BOLD | self.colors[1])
            except:
                pass
            
            mystic_time = AncientScript.get_mystic_time()
            time_x = width - len(mystic_time) - 2
            if time_x > 0:
                try:
                    screen.addstr(0, time_x, mystic_time, curses.A_DIM)
                except:
                    pass
            
            y = 2
            spirits = sorted(self.entities.values(), 
                           key=lambda e: e.rx_rate + e.tx_rate, 
                           reverse=True)
            
            for spirit in spirits[:self.config.max_spirits]:
                if y < height - 10:
                    self.draw_spirit_info(screen, spirit, y)
                    y += 9
            
            self.draw_status_bar(screen, height, width)
            self.draw_whispers_panel(screen, height, width)
            
            screen.refresh()
            
        except curses.error:
            pass
    
    def draw_status_bar(self, screen, height: int, width: int):
        try:
            status_y = height - 3
            total_rx = sum(e.rx_rate for e in self.entities.values())
            total_tx = sum(e.tx_rate for e in self.entities.values())
            
            if self.config.ancient_script:
                total_rx_disp = AncientScript.encode_rate(total_rx)
                total_tx_disp = AncientScript.encode_rate(total_tx)
            else:
                total_rx_disp = self.format_rate(total_rx)
                total_tx_disp = self.format_rate(total_tx)
            
            status = f"Total Flow: {total_rx_disp} ╫ {total_tx_disp}"
            status += f" │ Spirits: {len(self.entities)}"
            status += f" │ {AncientScript.get_mystic_time()}"
            
            if len(status) > width - 4:
                status = status[:width - 4]
            
            status_x = max(0, (width - len(status)) // 2)
            try:
                screen.addstr(status_y, status_x, status, curses.A_DIM)
            except:
                pass
            
        except curses.error:
            pass
    
    def draw_whispers_panel(self, screen, height: int, width: int):
        if not self.config.show_whispers:
            return
            
        try:
            panel_width = min(50, width - 2)
            panel_x = width - panel_width - 1
            
            try:
                screen.addstr(1, panel_x, "╭─[Whispers]─", curses.A_DIM)
            except:
                pass
            
            whispers = self.whispers.get_recent_whispers(8)
            for i, whisper in enumerate(whispers):
                if i < height - 4:
                    line = whisper[:panel_width - 2]
                    try:
                        screen.addstr(2 + i, panel_x, f"│{line}", curses.A_DIM)
                    except:
                        pass
            
            for y in range(1, min(len(whispers) + 2, height - 2)):
                try:
                    screen.addstr(y, panel_x + panel_width, "│", curses.A_DIM)
                except:
                    pass
            
            end_y = min(len(whispers) + 2, height - 2)
            try:
                screen.addstr(end_y, panel_x, "╰" + "─" * (panel_width), curses.A_DIM)
            except:
                pass
            
        except curses.error:
            pass
    
    def run_ritual(self, screen):
        self.init_colors()
        
        curses.curs_set(0)
        curses.noecho()
        curses.cbreak()
        screen.nodelay(1)
        screen.timeout(100)
        
        self.running = True
        self.whispers.add_whisper("Mystic", "Beginning the ritual...", "INFO")
        
        while self.running:
            try:
                key = screen.getch()
                
                if key == ord('q'):
                    self.running = False
                elif key == ord(' '):
                    self.perform_rituals()
                elif key == ord('r'):
                    self.whispers.add_whisper("Mystic", "Ritual refreshed", "INFO")
                elif key == ord('l'):
                    self.config.show_loopback = not self.config.show_loopback
                    status = "shown" if self.config.show_loopback else "hidden"
                    self.whispers.add_whisper("Mystic", f"Loopback spirits {status}", "INFO")
                elif key == ord('a'):
                    self.config.ancient_script = not self.config.ancient_script
                    status = "enabled" if self.config.ancient_script else "disabled"
                    self.whispers.add_whisper("Mystic", f"Ancient script {status}", "INFO")
                
                current_time = time.time()
                time_diff = current_time - self.last_update
                
                if time_diff >= self.config.update_interval:
                    self.scan_spirits()
                    self.perform_rituals()
                    self.draw_veil(screen)
                    self.last_update = current_time
                
                time.sleep(0.01)
                
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                self.whispers.add_whisper("Mystic", f"Error: {str(e)}", "ERROR")
                time.sleep(1)
    
    def save_mysteries(self):
        if not self.config.log_file:
            return
            
        try:
            mysteries = []
            for entity in self.entities.values():
                mystery = {
                    'spirit': entity.name,
                    'interface': entity.interface,
                    'essence': entity.essence,
                    'aura': entity.aura,
                    'total_rx': entity.rx_bytes,
                    'total_tx': entity.tx_bytes,
                    'whispers': entity.whispers[-5:],
                    'timestamp': datetime.now().isoformat()
                }
                mysteries.append(mystery)
            
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'mystic_time': AncientScript.get_mystic_time(),
                'total_spirits': len(self.entities),
                'mysteries': mysteries,
                'system_whispers': self.whispers.get_recent_whispers(10)
            }
            
            with open(self.config.log_file, 'a') as f:
                json.dump(log_entry, f, indent=2, ensure_ascii=False)
                f.write("\n")
                
        except Exception as e:
            self.whispers.add_whisper("Archivist", f"Failed to save: {str(e)}", "ERROR")
    
    def start(self):
        try:
            curses.wrapper(self.run_ritual)
        finally:
            self.cleanup()
    
    def cleanup(self):
        self.whispers.add_whisper("Mystic", "Ritual complete. Veil closing...", "INFO")
        self.save_mysteries()
        
        print(f"\nMysteries saved to {self.config.log_file}")
        print("\nMay the flows guide you...")
        print("\nControls:")
        print("  q - Quit")
        print("  Space - Perform ritual")
        print("  r - Refresh")
        print("  l - Toggle loopback spirits")
        print("  a - Toggle ancient script")

def main():
    config = MysticConfig()
    
    if len(sys.argv) > 1:
        config.load_from_file(sys.argv[1])
    
    mystic = NetworkMystic(config)
    
    atexit.register(mystic.cleanup)
    signal.signal(signal.SIGINT, lambda s, f: setattr(mystic, 'running', False))
    signal.signal(signal.SIGTERM, lambda s, f: setattr(mystic, 'running', False))
    
    mystic.start()

if __name__ == "__main__":
    main()
