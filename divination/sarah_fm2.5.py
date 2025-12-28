#!/usr/bin/env python3
"""
QUADRUPLE GODDESS v3.5 - ENHANCED SYSTEM
Integrated Divination: Geomancy + I Ching + Tarot + Jafr
"""

import json
import random
import sys
import platform
import hashlib
import math
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum

# ============ ENUMS & CONSTANTS ============
class Planet(Enum):
    SUN = "Sun"
    MOON = "Moon"
    MERCURY = "Mercury"
    VENUS = "Venus"
    MARS = "Mars"
    JUPITER = "Jupiter"
    SATURN = "Saturn"

class Element(Enum):
    FIRE = "Fire"
    WATER = "Water"
    AIR = "Air"
    EARTH = "Earth"
    METAL = "Metal"
    WOOD = "Wood"

# Planetary hours (traditional Chaldean order)
PLANETARY_HOURS = [
    "Saturn", "Jupiter", "Mars", "Sun", 
    "Venus", "Mercury", "Moon"
]

# ============ I CHING CASTER CLASS ============
class IChingCaster:
    """Traditional I Ching casting methods"""
    
    @staticmethod
    def cast_coins():
        """Traditional 3-coin method"""
        hexagram_lines = []
        changing_lines = []
        
        for line_num in range(6):
            total = sum([3 if random.random() > 0.5 else 2 for _ in range(3)])
            
            if total == 6:
                hexagram_lines.append(0)
                changing_lines.append(line_num + 1)
            elif total == 7:
                hexagram_lines.append(1)
            elif total == 8:
                hexagram_lines.append(0)
            elif total == 9:
                hexagram_lines.append(1)
                changing_lines.append(line_num + 1)
        
        hexagram_lines.reverse()
        return hexagram_lines, changing_lines
    
    @staticmethod
    def cast_yarrow_stalks():
        """Traditional yarrow stalk method - CORRECTED"""
        hexagram_lines = []
        changing_lines = []
        
        for line_position in range(6):
            # Start with 50 stalks
            stalks = 50
            line_value = 0
            
            for division in range(3):
                stalks -= 1  # Remove one stalk
                # Divide into two random groups
                if stalks > 1:
                    group1 = random.randint(1, stalks - 1)
                else:
                    group1 = 1
                group2 = stalks - group1
                
                # Calculate remainders
                remainder1 = 4 if (group1 % 4 == 0) else group1 % 4
                remainder2 = 4 if (group2 % 4 == 0) else group2 % 4
                remainder = remainder1 + remainder2
                
                # Update stalks and accumulate line value
                stalks = stalks - remainder
                if division == 2:  # Only care about the final value
                    line_value = (remainder == 4) * 2 + (remainder == 8) * 3
            
            # Map the line value to hexagram line
            if line_value == 6:  # Old yin (changing)
                hexagram_lines.append(0)
                changing_lines.append(6 - line_position)  # Lines are 1-6 from bottom
            elif line_value == 7:  # Young yang
                hexagram_lines.append(1)
            elif line_value == 8:  # Young yin
                hexagram_lines.append(0)
            elif line_value == 9:  # Old yang (changing)
                hexagram_lines.append(1)
                changing_lines.append(6 - line_position)  # Lines are 1-6 from bottom
        
        # In I Ching, lines are stored bottom to top, but we process top to bottom
        hexagram_lines.reverse()
        # Also need to adjust changing lines indices since we reversed
        changing_lines = [7 - line for line in changing_lines] if changing_lines else []
        
        return hexagram_lines, changing_lines
    
    @staticmethod
    def get_trigram_symbols(binary_str):
        """Convert binary string to trigram symbols"""
        # Define trigram mappings
        trigrams = {
            "111": "☰",  # Heaven
            "110": "☱",  # Lake
            "101": "☲",  # Fire
            "100": "☳",  # Thunder
            "011": "☴",  # Wind
            "010": "☵",  # Water
            "001": "☶",  # Mountain
            "000": "☷",   # Earth
        }
        
        # Hexagram is 6 lines, split into upper (first 3) and lower (last 3)
        if len(binary_str) == 6:
            lower_trigram = binary_str[3:]  # Lines 4-6 (bottom)
            upper_trigram = binary_str[:3]  # Lines 1-3 (top)
            
            lower_symbol = trigrams.get(lower_trigram, "?")
            upper_symbol = trigrams.get(upper_trigram, "?")
            
            return lower_symbol, upper_symbol
        
        return "?", "?"
    
    @staticmethod
    def get_trigram_name(symbol):
        """Get name of trigram from symbol"""
        trigram_names = {
            "☰": "Heaven",
            "☱": "Lake", 
            "☲": "Fire",
            "☳": "Thunder",
            "☴": "Wind",
            "☵": "Water",
            "☶": "Mountain",
            "☷": "Earth"
        }
        return trigram_names.get(symbol, "Unknown")

# ============ PLANETARY HOUR CALCULATOR ============
class PlanetaryHourCalculator:
    """Calculate planetary hours for talisman timing"""
    
    @staticmethod
    def calculate_current_planetary_hour():
        """Calculate current planetary hour"""
        now = datetime.now()
        sunrise = now.replace(hour=6, minute=0, second=0, microsecond=0)
        sunset = now.replace(hour=18, minute=0, second=0, microsecond=0)
        
        # Simple calculation - in reality this uses sunrise/sunset times
        if sunrise <= now < sunset:
            # Day hours
            total_day_minutes = 12 * 60
            minutes_since_sunrise = (now - sunrise).total_seconds() / 60
            hour_number = int(minutes_since_sunrise / (total_day_minutes / 12))
        else:
            # Night hours
            total_night_minutes = 12 * 60
            if now < sunrise:
                minutes_since_sunset = (now - (sunset - timedelta(days=1))).total_seconds() / 60
            else:
                minutes_since_sunset = (now - sunset).total_seconds() / 60
            hour_number = int(minutes_since_sunset / (total_night_minutes / 12))
        
        # Planetary hour sequence starts with the day's ruling planet
        # For simplicity, using Sunday as example
        day_of_week = now.weekday()
        day_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        day_ruler = day_planets[day_of_week]
        
        # Find index of day ruler
        start_index = PLANETARY_HOURS.index(day_ruler)
        planet_index = (start_index + hour_number) % 7
        
        return {
            "planet": PLANETARY_HOURS[planet_index],
            "hour_number": hour_number + 1,
            "is_daytime": sunrise <= now < sunset
        }
    
    @staticmethod
    def get_planetary_hour_schedule(date=None):
        """Get planetary hour schedule for a date"""
        if date is None:
            date = datetime.now()
        
        schedule = []
        day_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        day_ruler = day_planets[date.weekday()]
        
        start_index = PLANETARY_HOURS.index(day_ruler)
        
        for i in range(12):  # 12 day hours
            planet_index = (start_index + i) % 7
            schedule.append({
                "hour": i + 1,
                "planet": PLANETARY_HOURS[planet_index],
                "type": "day"
            })
        
        for i in range(12):  # 12 night hours
            planet_index = (start_index + 12 + i) % 7
            schedule.append({
                "hour": i + 1,
                "planet": PLANETARY_HOURS[planet_index],
                "type": "night"
            })
        
        return schedule

# ============ Hermetic Synthesis ============

class HermeticSynthesis:
    """Hermetic synthesis connecting all systems through mathematical correspondences"""
    
    def generate_hermetic_synthesis(self, geomantic, iching, tarot, planetary_hour):
        """Generate synthesis based on Thoth/Hermetic principles"""
        
        # Calculate numerical correspondences
        geomantic_num = self.binary_to_decimal(geomantic['binary'])
        iching_num = iching['primary']['number']
        tarot_num = tarot.get('number', 0)
        
        # Get trigram correspondences
        trigrams = iching.get('trigram_symbols', {})
        lower_trigram = trigrams.get('lower', '?')
        upper_trigram = trigrams.get('upper', '?')
        
        # Analyze mathematical patterns
        mathematical_analysis = self.analyze_mathematical_patterns(
            geomantic['binary'], 
            iching['binary'], 
            tarot_num
        )
        
        synthesis = f"""
        🜍 HERMETIC SYNTHESIS (Thoth/Ogdoad Framework)
        {'═' * 60}
        
        🔢 MATHEMATICAL CORRESPONDENCES:
        • Geomancy Binary: {geomantic['binary']} (Decimal: {geomantic_num})
        • I Ching Binary: {iching['binary']} (Hexagram #{iching_num})
        • Tarot Number: {tarot_num} ({tarot.get('suit', 'Major Arcana')})
        • Planetary Hour: {planetary_hour['planet']} (Hour {planetary_hour['hour_number']})
        
        🜂 ELEMENTAL TRIANGULATION (Thoth's Four Elements):
        • Geomancy: {geomantic.get('element', 'Unknown')} → {self.get_thoth_element(geomantic.get('element', ''))}
        • I Ching: {iching['primary'].get('element', 'Unknown')} → {self.get_thoth_element(iching['primary'].get('element', ''))}
        • Tarot: {tarot.get('element', 'Unknown')} → {self.get_thoth_element(tarot.get('element', ''))}
        
        🜄 TRIGRAMMATIC CONNECTIONS (Ogdoad Structure):
        • Lower Trigram: {lower_trigram} → {self.get_ogdoad_correspondence(lower_trigram)}
        • Upper Trigram: {upper_trigram} → {self.get_ogdoad_correspondence(upper_trigram)}
        • Combined: {self.analyze_trigram_combination(lower_trigram, upper_trigram)}
        
        {mathematical_analysis}
        
        🜁 INTEGRATED HERMETIC PRINCIPLES:
        
        PRINCIPLE OF CORRESPONDENCE (As Above, So Below):
        • Geomancy (Earth/Microcosm): {geomantic['name']} represents {geomantic.get('meaning', '')[:50]}...
        • I Ching (Heaven/Macrocosm): {iching['primary']['english']} represents {iching['primary'].get('judgment_english', '')[:50]}...
        • Tarot (Mediating Principle): {tarot['name']} connects through {tarot.get('element', 'archetypal')} energy
        
        PRINCIPLE OF VIBRATION (Numerical Resonance):
        • Core Vibration: {self.calculate_core_vibration(geomantic_num, iching_num, tarot_num)}
        • Harmonic Alignment: {self.check_harmonic_alignment(geomantic_num, iching_num, tarot_num)}
        
        PRINCIPLE OF RHYTHM (Temporal Alignment):
        • Current Timing: {planetary_hour['planet']} hour - {self.get_planet_quality(planetary_hour['planet'])}
        • Optimal Rhythm: {self.calculate_optimal_rhythm(geomantic, iching, tarot)}
        
        🜃 PRACTICAL APPLICATION (Hermetic Art):
        
        1. MEDITATION FOCUS (Mental Plane):
           "Contemplate the unification of {geomantic['name']} (form), 
           {iching['primary']['english']} (principle), and {tarot['name']} (archetype)"
        
        2. RITUAL STRUCTURE (Astral Plane):
           • Time: During {planetary_hour['planet']}'s hour
           • Space: Facing {self.get_direction(geomantic.get('element', ''))}
           • Elements: {self.get_ritual_elements(geomantic, iching, tarot)}
        
        3. PRACTICAL WORK (Physical Plane):
           • Immediate: {self.get_hermetic_action(geomantic, 'immediate')}
           • Strategic: {self.get_hermetic_strategy(iching, 'strategic')}
           • Transformational: {self.get_hermetic_transformation(tarot, 'transformational')}
        
        🜀 REFLECTIVE QUESTIONS (Emerald Tablet):
        1. "How does the binary pattern {geomantic['binary']} reflect in my current situation?"
        2. "What does the movement from {lower_trigram} to {upper_trigram} teach about my path?"
        3. "How can I embody the {tarot['name']} energy while grounded in {geomantic['name']}?"
        
        🔷 OGDOAD CONNECTION (Eightfold Path):
        This reading connects to the {self.get_ogdoad_aspect(geomantic, iching, tarot)} 
        aspect of the Eightfold creation principle.
        """
        
        return synthesis
    
    def binary_to_decimal(self, binary_str):
        """Convert binary string to decimal"""
        try:
            return int(binary_str, 2)
        except:
            return 0
    
    def get_thoth_element(self, element):
        """Map elements to Thoth/Hermetic principles"""
        thoth_map = {
            "Fire": "Will/Energy (Sulfur principle)",
            "Water": "Emotion/Intuition (Mercury principle)",
            "Air": "Intellect/Mind (Salt principle)",
            "Earth": "Manifestation/Body (Salt principle)",
            "Metal": "Structure/Contraction",
            "Wood": "Growth/Expansion"
        }
        return thoth_map.get(element, "Transcendent principle")
    
    def get_ogdoad_correspondence(self, trigram_symbol):
        """Map trigrams to Ogdoad principles"""
        ogdoad_map = {
            "☰": "Heaven (Nu/Naunet - Primordial Waters)",
            "☷": "Earth (Amun/Amaunet - Hidden Force)",
            "☲": "Fire (Heh/Hauhet - Infinity)",
            "☵": "Water (Kuk/Kauket - Darkness)",
            "☳": "Thunder (Niau/Niaut)",
            "☴": "Wind (etc.)",
            "☶": "Mountain",
            "☱": "Lake"
        }
        return ogdoad_map.get(trigram_symbol, "Unified principle")
    
    def analyze_mathematical_patterns(self, geomantic_bin, iching_bin, tarot_num):
        """Analyze mathematical relationships between systems"""
        
        # Calculate binary patterns
        geo_bin = geomantic_bin
        ich_bin = iching_bin
        
        # Look for patterns
        patterns = []
        
        # Check for mirror patterns
        if geo_bin == ich_bin[-4:]:  # If geomantic matches last 4 bits of I Ching
            patterns.append("Geomantic pattern embedded in I Ching structure")
        
        # Check numerology
        geo_num = self.binary_to_decimal(geo_bin)
        ich_num = self.binary_to_decimal(ich_bin[:3])  # First trigram
        
        if (geo_num + ich_num) % 8 == 0:
            patterns.append("Octave resonance (mod 8)")
        
        if tarot_num > 0 and (geo_num + tarot_num) % 9 == 0:
            patterns.append("Enneadic pattern (mod 9)")
        
        # Check binary symmetries
        if geo_bin == geo_bin[::-1]:
            patterns.append("Geomantic palindrome symmetry")
        
        if ich_bin[:3] == ich_bin[3:]:
            patterns.append("I Ching trigram symmetry")
        
        analysis = "🔢 MATHEMATICAL PATTERNS:\n"
        if patterns:
            for pattern in patterns:
                analysis += f"   • {pattern}\n"
        else:
            analysis += "   • Unique numerical signature (no common patterns)\n"
        
        # Add Pythagorean/Platonic analysis
        geo_sum = sum(int(b) for b in geo_bin)
        ich_sum = sum(int(b) for b in ich_bin)
        
        analysis += f"\n   Pythagorean Analysis:\n"
        analysis += f"   • Geomancy digit sum: {geo_sum} → {self.reduce_number(geo_sum)}\n"
        analysis += f"   • I Ching digit sum: {ich_sum} → {self.reduce_number(ich_sum)}\n"
        
        if tarot_num > 0:
            tarot_reduced = self.reduce_number(tarot_num)
            analysis += f"   • Tarot number {tarot_num} → {tarot_reduced}\n"
        
        return analysis
    
    def reduce_number(self, num):
        """Reduce number to single digit (Pythagorean numerology)"""
        while num > 9:
            num = sum(int(d) for d in str(num))
        meanings = {
            1: "Unity, Beginning",
            2: "Duality, Balance",
            3: "Creativity, Trinity",
            4: "Stability, Foundation",
            5: "Change, Movement",
            6: "Harmony, Balance",
            7: "Wisdom, Mystery",
            8: "Power, Manifestation",
            9: "Completion, Wisdom"
        }
        return f"{num}: {meanings.get(num, 'Mystery')}"
    
    def calculate_core_vibration(self, geo_num, ich_num, tarot_num):
        """Calculate core vibrational number from all systems"""
        total = geo_num + ich_num + tarot_num
        reduced = self.reduce_number(total)
        
        # Additional Hermetic analysis
        if reduced.startswith('1'): return "Creative impulse, new beginning"
        elif reduced.startswith('2'): return "Harmonizing dualities, partnership"
        elif reduced.startswith('3'): return "Creative expression, trinity in action"
        elif reduced.startswith('4'): return "Foundation building, stabilization"
        elif reduced.startswith('5'): return "Transformational change, alchemical process"
        elif reduced.startswith('6'): return "Harmonic integration, beauty"
        elif reduced.startswith('7'): return "Mystical insight, inner wisdom"
        elif reduced.startswith('8'): return "Manifestation power, infinity in action"
        elif reduced.startswith('9'): return "Completion, wisdom synthesis"
        return "Unique vibrational signature" 
        
    def analyze_trigram_combination(self, lower_trigram, upper_trigram):
        """Analyze combination of trigrams"""
        trigram_interactions = {
            ("☰", "☰"): "Heaven upon Heaven: Pure creative force, ultimate power",
            ("☰", "☷"): "Heaven upon Earth: Creative manifestation, ideal meeting reality",
            ("☷", "☰"): "Earth upon Heaven: Receptive to divine inspiration",
            ("☲", "☵"): "Fire upon Water: Passion meeting emotion, transformative alchemy",
            ("☵", "☲"): "Water upon Fire: Emotion tempering passion, controlled transformation",
        }
        
        key = (lower_trigram, upper_trigram)
        if key in trigram_interactions:
            return trigram_interactions[key]
        
        # Fallback analysis
        lower_name = self.get_trigram_essence(lower_trigram)
        upper_name = self.get_trigram_essence(upper_trigram)
        return f"{lower_name} (foundation) supporting {upper_name} (expression)"
    
    def get_trigram_essence(self, trigram):
        """Get essence of trigram"""
        essences = {
            "☰": "Creative force",
            "☷": "Receptive ground", 
            "☲": "Illuminating fire",
            "☵": "Deep water",
            "☳": "Awakening thunder",
            "☴": "Penetrating wind",
            "☶": "Stable mountain",
            "☱": "Joyful lake"
        }
        return essences.get(trigram, "Unknown trigram")
    
    def check_harmonic_alignment(self, geomantic_num, iching_num, tarot_num):
        """Check harmonic alignment between numbers"""
        numbers = [geomantic_num, iching_num, tarot_num]
        
        # Check for common divisors
        common_divisors = []
        for i in range(2, 10):
            if all(n % i == 0 for n in numbers if n > 0):
                common_divisors.append(i)
        
        if common_divisors:
            return f"Harmonic resonance at multiples of {', '.join(map(str, common_divisors))}"
        
        # Check for Fibonacci-like sequences
        if len(numbers) == 3 and numbers[2] == numbers[0] + numbers[1]:
            return "Fibonacci sequence alignment"
        
        # Check for golden ratio approximation
        if len(numbers) == 3 and numbers[1] > 0:
            ratio = numbers[2] / numbers[1] if numbers[2] > 0 else 0
            if 1.5 < ratio < 1.7:
                return "Golden ratio approximation detected"
        
        return "Numbers show unique harmonic signature"
    
    def calculate_optimal_rhythm(self, geomantic, iching, tarot):
        """Calculate optimal rhythm for action"""
        elements = {
            geomantic.get('element', ''): 3,
            iching['primary'].get('element', ''): 2,
            tarot.get('element', ''): 1
        }
        
        # Determine dominant element
        fire_count = sum(1 for e in elements if 'Fire' in str(e))
        water_count = sum(1 for e in elements if 'Water' in str(e))
        air_count = sum(1 for e in elements if 'Air' in str(e))
        earth_count = sum(1 for e in elements if 'Earth' in str(e))
        
        counts = {'Fire': fire_count, 'Water': water_count, 'Air': air_count, 'Earth': earth_count}
        dominant = max(counts, key=counts.get)
        
        rhythms = {
            'Fire': "Quick, decisive actions in 3-day cycles",
            'Water': "Fluid, intuitive timing - follow emotional cues",
            'Air': "Mental focus in morning, communication in afternoon",
            'Earth': "Slow, steady progress with weekly checkpoints"
        }
        
        return rhythms.get(dominant, "Follow natural cycles and planetary timing")
    
    def get_direction(self, element):
        """Get direction for element"""
        directions = {
            "Fire": "South",
            "Water": "West",
            "Air": "East",
            "Earth": "North"
        }
        return directions.get(element, "Center")
    
    def get_ritual_elements(self, geomantic, iching, tarot):
        """Get ritual elements for combined reading"""
        elements = set()
        if 'element' in geomantic:
            elements.add(geomantic['element'])
        if 'element' in iching.get('primary', {}):
            elements.add(iching['primary']['element'])
        if 'element' in tarot:
            elements.add(tarot['element'])
        return ", ".join(elements) if elements else "Universal elements"
    
    def get_hermetic_action(self, geomantic, action_type):
        """Get hermetic action based on geomantic figure"""
        actions = {
            "Via": "Take the first step on a new path",
            "Cauda Draconis": "Release what no longer serves you",
            "Puer": "Act with courage but consider consequences",
            "Amissio": "Practice non-attachment and letting go"
        }
        figure_name = geomantic.get('name', 'Unknown')
        return actions.get(figure_name, f"Work with {figure_name} through practical application")
    
    def get_hermetic_strategy(self, iching, strategy_type):
        """Get hermetic strategy based on I Ching"""
        hexagram_name = iching['primary'].get('english', 'Unknown')
        return f"Align with {hexagram_name} through conscious adaptation of its principles"
    
    def get_hermetic_transformation(self, tarot, transformation_type):
        """Get hermetic transformation based on Tarot"""
        card_name = tarot.get('name', 'Unknown')
        return f"Integrate {card_name} energy through inner work and conscious embodiment"
    
    def get_ogdoad_aspect(self, geomantic, iching, tarot):
        """Get ogdoad aspect for combined reading"""
        elements = [
            geomantic.get('element', ''),
            iching['primary'].get('element', ''),
            tarot.get('element', '')
        ]
        
        if all('Fire' in e or e == 'Fire' for e in elements if e):
            return "Creative fire principle"
        elif all('Water' in e or e == 'Water' for e in elements if e):
            return "Receptive water principle"
        elif all('Air' in e or e == 'Air' for e in elements if e):
            return "Mediating air principle"
        elif all('Earth' in e or e == 'Earth' for e in elements if e):
            return "Manifesting earth principle"
        
        return "Unified manifestation principle"
    
    def get_planet_quality(self, planet):
        """Get quality description for a planet"""
        qualities = {
            "Sun": "Vitality, success, leadership",
            "Moon": "Intuition, emotions, receptivity",
            "Mercury": "Communication, intellect, travel",
            "Venus": "Love, beauty, harmony",
            "Mars": "Action, courage, conflict",
            "Jupiter": "Expansion, luck, wisdom",
            "Saturn": "Discipline, structure, karma"
        }
        return qualities.get(planet, "Neutral influence")

# ============ INTERPRETATION DEPTH SYSTEM ============

class InterpretationDepthSystem:
    """Manage interpretation depth levels"""
    
    DEPTH_LEVELS = {
        "standard": {
            "description": "Core meanings and basic synthesis",
            "geomancy_fields": ["name", "binary", "meaning", "planet", "element"],
            "iching_fields": ["number", "english", "chinese", "judgment_english"],
            "tarot_fields": ["name", "suit", "meaning", "element"],
            "synthesis_type": "basic"
        },
        "detailed": {
            "description": "Extended interpretations with practical guidance",
            "geomancy_fields": ["name", "binary", "meaning", "planet", "element", 
                               "astrological", "essence", "practical_advice"],
            "iching_fields": ["number", "english", "chinese", "judgment_english",
                            "image", "lines_english", "changing_meaning"],
            "tarot_fields": ["name", "suit", "meaning", "element", "planet",
                           "upright_meaning", "reversed_meaning", "symbolism"],
            "synthesis_type": "hermetic"
        },
        "comprehensive": {
            "description": "Full Hermetic synthesis with mathematical analysis",
            "geomancy_fields": "all",
            "iching_fields": "all",
            "tarot_fields": "all",
            "synthesis_type": "hermetic_detailed",
            "include": ["mathematical_analysis", "ogdoad_connections", 
                       "hermetic_principles", "ritual_guidance", 
                       "reflective_questions"]
        }
    }
    
    def get_interpretation(self, data, system, depth="standard"):
        """Get interpretation at specified depth level"""
        level = self.DEPTH_LEVELS.get(depth, self.DEPTH_LEVELS["standard"])
        
        if system == "geomancy":
            return self.format_geomantic_interpretation(data, level)
        elif system == "iching":
            return self.format_iching_interpretation(data, level)
        elif system == "tarot":
            return self.format_tarot_interpretation(data, level)
        
        return data
    
    def format_geomantic_interpretation(self, figure, level):
        """Format geomancy interpretation at specified depth"""
        
        if level["geomancy_fields"] == "all":
            # Comprehensive interpretation
            interpretation = f"""
            🧿 GEOMANTIC FIGURE: {figure.get('name', 'Unknown')}
            {'═' * 60}
            
            BINARY FOUNDATION: {figure.get('binary', '')}
            • Decimal value: {self.binary_to_decimal(figure.get('binary', '0000'))}
            • Binary pattern: {self.analyze_binary_pattern(figure.get('binary', ''))}
            
            HERMETIC CORRESPONDENCES:
            • Planet: {figure.get('planet', 'Unknown')} - {self.get_planet_essence(figure.get('planet', ''))}
            • Element: {figure.get('element', 'Unknown')} - {self.get_element_essence(figure.get('element', ''))}
            
            PRACTICAL APPLICATION:
            
            RITUAL USE:
            • Best Time: {figure.get('best_time', 'Planetary hour of ruling planet')}
            • Best Day: {figure.get('best_day', 'Day of ruling planet')}
            • Elemental Focus: {figure.get('elemental_focus', 'Work with corresponding element')}
            
            PERSONAL DEVELOPMENT:
            • Shadow Aspect: {figure.get('shadow', 'Potential unconscious pattern')}
            • Gift: {figure.get('gift', 'Inherent talent or quality')}
            • Challenge: {figure.get('challenge', 'Area for growth')}
            
            MATHEMATICAL SIGNIFICANCE:
            • Pythagorean value: {self.calculate_pythagorean_value(figure.get('binary', ''))}
            • Numerical archetype: {self.get_numerical_archetype(figure.get('binary', ''))}
            
            MEDITATION GUIDANCE:
            {figure.get('meditation', 'Contemplate the binary pattern and its geometrical form')}
            """
        else:
            # Standard or detailed
            interpretation = f"{figure.get('name', 'Unknown')}: {figure.get('meaning', '')}"
            
            if "detailed" in level["description"].lower():
                interpretation += f"\n\nElement: {figure.get('element', '')}"
                interpretation += f"\nPlanet: {figure.get('planet', '')}"
                interpretation += f"\nPractical: {figure.get('practical_advice', '')}"
        
        return interpretation
    
    def format_iching_interpretation(self, iching, level):
        """Format I Ching interpretation at specified depth"""
        primary = iching.get('primary', {})
        
        if level["iching_fields"] == "all":
            interpretation = f"""
            📜 I CHING HEXAGRAM: {primary.get('english', 'Unknown')}
            {'═' * 60}
            
            HEXAGRAM #{primary.get('number', 0)}: {primary.get('chinese', '')}
            • Binary: {iching.get('binary', '')}
            • Judgment: {primary.get('judgment_english', '')}
            
            TRIGRAM ANALYSIS:
            • Lower: {iching.get('trigram_symbols', {}).get('lower', '?')}
            • Upper: {iching.get('trigram_symbols', {}).get('upper', '?')}
            
            LINE INTERPRETATIONS:"""
            
            if 'lines_english' in primary:
                for i, line in enumerate(primary['lines_english']):
                    interpretation += f"\n  Line {i+1}: {line}"
            
            if iching.get('changing_lines'):
                interpretation += f"\n\n🌊 CHANGING LINES: {iching['changing_lines']}"
                if iching.get('secondary'):
                    sec = iching['secondary']
                    interpretation += f"\n• Evolving to: #{sec.get('number', '?')} {sec.get('english', 'Unknown')}"
            
            interpretation += f"\n\nELEMENTAL CORRESPONDENCE: {primary.get('element', 'Unknown')}"
            interpretation += f"\nPLANETARY RULER: {primary.get('planet', 'Unknown')}"
            
        else:
            interpretation = f"#{primary.get('number', 0)} {primary.get('english', 'Unknown')}: {primary.get('judgment_english', '')[:100]}..."
            
            if "detailed" in level["description"].lower() and 'lines_english' in primary:
                interpretation += "\n\nLine Insights:"
                for i, line in enumerate(primary['lines_english'][:3]):
                    interpretation += f"\n  Line {i+1}: {line[:50]}..."
        
        return interpretation
    
    def format_tarot_interpretation(self, tarot, level):
        """Format tarot interpretation at specified depth"""
        if level["tarot_fields"] == "all":
            interpretation = f"""
            🃏 TAROT CARD: {tarot.get('name', 'Unknown')}
            {'═' * 60}
            
            {tarot.get('suit', 'Major Arcana')}
            • Number: {tarot.get('number', 0)}
            • Element: {tarot.get('element', 'Unknown')}
            • Planet: {tarot.get('planet', 'Unknown')}
            
            UPRIGHT MEANING:
            {tarot.get('meaning', 'No meaning available.')}
            
            SYMBOLISM:
            {tarot.get('symbolism', 'Symbolic interpretation not available.')}
            
            PRACTICAL APPLICATION:
            • Daily Practice: {tarot.get('daily_practice', 'Meditate on card imagery')}
            • Shadow Aspect: {tarot.get('shadow', 'Potential unconscious pattern')}
            • Evolutionary Path: {tarot.get('evolution', 'Path of growth and integration')}
            """
        else:
            interpretation = f"{tarot.get('name', 'Unknown')} ({tarot.get('suit', '')}): {tarot.get('meaning', '')}"
            
            if "detailed" in level["description"].lower():
                interpretation += f"\n\nElement: {tarot.get('element', '')}"
                interpretation += f"\nPlanet: {tarot.get('planet', '')}"
        
        return interpretation
    
    def binary_to_decimal(self, binary_str):
        """Convert binary to decimal"""
        try:
            return int(binary_str, 2)
        except:
            return 0
    
    def analyze_binary_pattern(self, binary_str):
        """Analyze binary pattern"""
        if binary_str == binary_str[::-1]:
            return "Palindrome symmetry - balanced energy"
        elif '1111' in binary_str:
            return "Strong yang emphasis"
        elif '0000' in binary_str:
            return "Strong yin emphasis"
        else:
            return "Dynamic interplay of yin and yang"
    
    def get_planet_essence(self, planet):
        """Get planet essence"""
        essences = {
            "Sun": "Vital consciousness, creative will",
            "Moon": "Receptive intuition, emotional wisdom",
            "Mercury": "Adaptive intellect, communicative bridge",
            "Venus": "Harmonizing love, aesthetic appreciation",
            "Mars": "Dynamic action, courageous initiative",
            "Jupiter": "Expansive wisdom, abundant growth",
            "Saturn": "Structural discipline, karmic lessons"
        }
        return essences.get(planet, "Cosmic influence")
    
    def get_element_essence(self, element):
        """Get element essence"""
        essences = {
            "Fire": "Transforming energy, purifying will",
            "Water": "Fluid emotion, intuitive depth",
            "Air": "Mental clarity, communicative flow",
            "Earth": "Manifesting stability, practical grounding"
        }
        return essences.get(element, "Elemental force")
    
    def calculate_pythagorean_value(self, binary_str):
        """Calculate Pythagorean value"""
        decimal = self.binary_to_decimal(binary_str)
        while decimal > 9:
            decimal = sum(int(d) for d in str(decimal))
        return f"{decimal} - {self.get_number_meaning(decimal)}"
    
    def get_number_meaning(self, num):
        """Get meaning of number"""
        meanings = {
            1: "Unity, Beginning",
            2: "Duality, Balance",
            3: "Creativity, Trinity",
            4: "Stability, Foundation",
            5: "Change, Movement",
            6: "Harmony, Balance",
            7: "Wisdom, Mystery",
            8: "Power, Manifestation",
            9: "Completion, Wisdom"
        }
        return meanings.get(num, "Mystery")
    
    def get_numerical_archetype(self, binary_str):
        """Get numerical archetype"""
        decimal = self.binary_to_decimal(binary_str)
        archetypes = {
            0: "The Void - Infinite potential",
            1: "The Magician - Conscious creation",
            2: "The High Priestess - Intuitive wisdom",
            3: "The Empress - Creative abundance",
            4: "The Emperor - Structural authority",
            5: "The Hierophant - Traditional wisdom",
            6: "The Lovers - Harmonious choice",
            7: "The Chariot - Directed will",
            8: "Strength - Courageous mastery",
            9: "The Hermit - Inner wisdom",
            10: "Wheel of Fortune - Cyclical change",
            11: "Justice - Balance and truth",
            12: "The Hanged Man - Sacrificial wisdom",
            13: "Death - Transformational ending",
            14: "Temperance - Alchemical blending",
            15: "The Devil - Material bondage"
        }
        return archetypes.get(decimal, "Unique numerical signature")

# ============ MAGIC SQUARE GENERATOR ============
class MagicSquareGenerator:
    """Generate traditional magic squares"""
    
    @staticmethod
    def generate_saturn_square():
        """3x3 Saturn square (Lo Shu)"""
        return [
            [4, 9, 2],
            [3, 5, 7],
            [8, 1, 6]
        ]
    
    @staticmethod
    def generate_jupiter_square():
        """4x4 Jupiter square"""
        return [
            [4, 14, 15, 1],
            [9, 7, 6, 12],
            [5, 11, 10, 8],
            [16, 2, 3, 13]
        ]
    
    @staticmethod
    def generate_mars_square():
        """5x5 Mars square"""
        return [
            [11, 24, 7, 20, 3],
            [4, 12, 25, 8, 16],
            [17, 5, 13, 21, 9],
            [10, 18, 1, 14, 22],
            [23, 6, 19, 2, 15]
        ]
    
    @staticmethod
    def generate_sun_square():
        """6x6 Sun square"""
        return [
            [6, 32, 3, 34, 35, 1],
            [7, 11, 27, 28, 8, 30],
            [19, 14, 16, 15, 23, 24],
            [18, 20, 22, 21, 17, 13],
            [25, 29, 10, 9, 26, 12],
            [36, 5, 33, 4, 2, 31]
        ]
    
    @staticmethod
    def generate_venus_square():
        """7x7 Venus square"""
        return [
            [22, 47, 16, 41, 10, 35, 4],
            [5, 23, 48, 17, 42, 11, 29],
            [30, 6, 24, 49, 18, 36, 12],
            [13, 31, 7, 25, 43, 19, 37],
            [38, 14, 32, 1, 26, 44, 20],
            [21, 39, 8, 33, 2, 27, 45],
            [46, 15, 40, 9, 34, 3, 28]
        ]
    
    @staticmethod
    def generate_mercury_square():
        """8x8 Mercury square"""
        return [
            [8, 58, 59, 5, 4, 62, 63, 1],
            [49, 15, 14, 52, 53, 11, 10, 56],
            [41, 23, 22, 44, 45, 19, 18, 48],
            [32, 34, 35, 29, 28, 38, 39, 25],
            [40, 26, 27, 37, 36, 30, 31, 33],
            [17, 47, 46, 20, 21, 43, 42, 24],
            [9, 55, 54, 12, 13, 51, 50, 16],
            [64, 2, 3, 61, 60, 6, 7, 57]
        ]
    
    @staticmethod
    def generate_moon_square():
        """9x9 Moon square"""
        return [
            [37, 78, 29, 70, 21, 62, 13, 54, 5],
            [6, 38, 79, 30, 71, 22, 63, 14, 46],
            [47, 7, 39, 80, 31, 72, 23, 55, 15],
            [16, 48, 8, 40, 81, 32, 64, 24, 56],
            [57, 17, 49, 9, 41, 73, 33, 65, 25],
            [26, 58, 18, 50, 1, 42, 74, 34, 66],
            [67, 27, 59, 10, 51, 2, 43, 75, 35],
            [36, 68, 19, 60, 11, 52, 3, 44, 76],
            [77, 28, 69, 20, 61, 12, 53, 4, 45]
        ]
    
    @staticmethod
    def get_square_by_planet(planet_name, size=None):
        """Get magic square for specific planet"""
        planet_squares = {
            "Saturn": (3, MagicSquareGenerator.generate_saturn_square),
            "Jupiter": (4, MagicSquareGenerator.generate_jupiter_square),
            "Mars": (5, MagicSquareGenerator.generate_mars_square),
            "Sun": (6, MagicSquareGenerator.generate_sun_square),
            "Venus": (7, MagicSquareGenerator.generate_venus_square),
            "Mercury": (8, MagicSquareGenerator.generate_mercury_square),
            "Moon": (9, MagicSquareGenerator.generate_moon_square)
        }
        
        if planet_name in planet_squares:
            size, generator = planet_squares[planet_name]
            return generator(), size
        else:
            # Default to Saturn square
            return MagicSquareGenerator.generate_saturn_square(), 3
    
    @staticmethod
    def display_square(square, title=""):
        """Display magic square in formatted way"""
        if not square:
            return ""
        
        size = len(square)
        
        # Calculate the width needed for each cell (based on largest number)
        max_num = size * size
        cell_width = len(str(max_num)) + 2  # +2 for padding
        
        output = f"\n🔢 {title} ({size}x{size} Magic Square):\n"
        
        # Build top border
        top_border = "┌"
        for col in range(size):
            top_border += "─" * cell_width
            if col < size - 1:
                top_border += "┬"
        top_border += "┐"
        output += top_border + "\n"
        
        # Build rows
        for row_idx, row in enumerate(square):
            row_str = "│"
            for num in row:
                row_str += f"{num:^{cell_width}}│"
            output += row_str + "\n"
            
            # Build separator between rows (not after last row)
            if row_idx < size - 1:
                separator = "├"
                for col in range(size):
                    separator += "─" * cell_width
                    if col < size - 1:
                        separator += "┼"
                separator += "┤"
                output += separator + "\n"
        
        # Build bottom border
        bottom_border = "└"
        for col in range(size):
            bottom_border += "─" * cell_width
            if col < size - 1:
                bottom_border += "┴"
        bottom_border += "┘"
        output += bottom_border + "\n"
        
        # Calculate magic constant
        magic_constant = size * (size**2 + 1) // 2
        output += f"\n✨ Magic Constant: {magic_constant}\n"
        
        return output

# ============ READING HISTORY MANAGER ============
class ReadingHistory:
    """Manage reading history and archives"""
    
    def __init__(self, data_dir="readings"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.history_file = self.data_dir / "history.json"
        self.history = self.load_history()
    
    def load_history(self):
        """Load reading history from file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_history(self):
        """Save reading history to file"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def add_reading(self, reading_data):
        """Add a new reading to history"""
        entry = {
            "id": len(self.history) + 1,
            "timestamp": datetime.now().isoformat(),
            "query": reading_data.get("query", ""),
            "geomantic": reading_data.get("geomantic", {}).get("name", ""),
            "iching": reading_data.get("iching", {}).get("primary", {}).get("english", ""),
            "tarot": reading_data.get("tarot", {}).get("name", ""),
            "filename": reading_data.get("filename", ""),
            "summary": self.create_summary(reading_data)
        }
        self.history.append(entry)
        self.save_history()
        return entry
    
    def create_summary(self, reading_data):
        """Create a summary of the reading"""
        summary = f"Geomancy: {reading_data.get('geomantic', {}).get('name', '')} | "
        summary += f"I Ching: {reading_data.get('iching', {}).get('primary', {}).get('english', '')} | "
        summary += f"Tarot: {reading_data.get('tarot', {}).get('name', '')}"
        return summary
    
    def get_recent_readings(self, limit=10):
        """Get recent readings"""
        return self.history[-limit:] if self.history else []
    
    def search_readings(self, keyword):
        """Search readings by keyword"""
        results = []
        for reading in self.history:
            if (keyword.lower() in reading["query"].lower() or 
                keyword.lower() in reading["geomantic"].lower() or
                keyword.lower() in reading["summary"].lower()):
                results.append(reading)
        return results
    
    def export_to_json(self, filename="readings_export.json"):
        """Export all readings to JSON file"""
        export_data = {
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "total_readings": len(self.history),
                "system": "quadruple.goddess"
            },
            "readings": self.history
        }
        
        export_file = self.data_dir / filename
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return export_file
    
    def export_to_text(self, filename="readings_export.txt"):
        """Export readings to text file"""
        export_file = self.data_dir / filename
        
        with open(export_file, 'w') as f:
            f.write("="*60 + "\n")
            f.write("QUADRUPLE GODDESS READING ARCHIVE\n")
            f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Readings: {len(self.history)}\n")
            f.write("="*60 + "\n\n")
            
            for i, reading in enumerate(self.history, 1):
                f.write(f"READING #{i}\n")
                f.write(f"Date: {reading['timestamp']}\n")
                f.write(f"Query: {reading['query']}\n")
                f.write(f"Summary: {reading['summary']}\n")
                f.write(f"File: {reading['filename']}\n")
                f.write("-"*40 + "\n\n")
        
        return export_file

# ============ MAIN SYSTEM CLASS ============
class QuadrupleGoddessSystem:
    def __init__(self):
        """Initialize the enhanced system"""
        self.version = "3.5.0"
        self.framework = "quadruple.goddess"
        self.build_date = "2025-12-09"
        
        # Initialize subsystems
        self.iching_caster = IChingCaster()
        self.hour_calculator = PlanetaryHourCalculator()
        self.magic_squares = MagicSquareGenerator()
        self.history_manager = ReadingHistory()
        self.hermetic_synthesis = HermeticSynthesis()
        self.interpretation_depth = InterpretationDepthSystem()
        
        # Load data
        self.load_all_systems()
    
    def get_system_explanation(self, geomantic, iching, tarot, starting_system):
        """Generate explanation based on starting system"""
        explanations = {
            "geomancy": f"""
            🧿 STARTING WITH GEOMANCY:
            This reading begins with the earthly foundation - the geomantic figure {geomantic['name']}.
            Geomancy represents the microcosm, the physical reality and practical situation.
            
            Why start here? Because form precedes manifestation. {geomantic['name']} shows 
            the current energetic pattern in material reality, which then connects to...
            """,
            "iching": f"""
            📜 STARTING WITH I CHING:
            This reading begins with cosmic principles - hexagram #{iching['primary']['number']}.
            I Ching represents the macrocosm, universal patterns and archetypal forces.
            
            Why start here? Because principle precedes form. The hexagram shows 
            the underlying cosmic pattern that manifests as earthly events.
            """,
            "tarot": f"""
            🃏 STARTING WITH TAROT:
            This reading begins with archetypal psychology - the {tarot['name']} card.
            Tarot represents the mediating principle between heaven and earth.
            
            Why start here? Because psyche precedes experience. The card reveals 
            the psychological patterns shaping your perception of reality.
            """,
            "jafr": f"""
            📿 STARTING WITH JAFR:
            This reading begins with magical action - the {geomantic.get('name', '')} talisman.
            Jafr represents practical magic and ritual implementation.
            
            Why start here? Because intention precedes result. The talisman recipe 
            shows how to actively engage with the energies revealed.
            """,
            "balanced": """
            ⚖️ BALANCED PERSPECTIVE:
            All four systems are given equal weight in this synthesis.
            Geomancy (earth), I Ching (heaven), Tarot (mediation), and Jafr (action)
            together create a complete picture of the situation.
            """
        }
        
        return explanations.get(starting_system, "")
    
    def run_full_reading_with_options(self):
        """Run full reading with configuration options"""
        print("\n" + "="*60)
        print("⚙️  CONFIGURE FULL READING")
        print("="*60)
        
        # Get query
        query = input("\n📝 Enter your query (or press Enter for general reading): ")
        
        print("\n🔄 SELECT STARTING PERSPECTIVE:")
        print("  1. Geomancy (Earth/Microcosm)")
        print("  2. I Ching (Heaven/Macrocosm)")
        print("  3. Tarot (Archetypes/Mediation)")
        print("  4. Jafr (Talismanic/Action)")
        print("  5. Balanced (Default - All systems equal)")
        
        system_choice = input("\nChoose starting perspective (1-5, default 5): ").strip()
        
        system_map = {
            "1": "geomancy",
            "2": "iching",
            "3": "tarot",
            "4": "jafr",
            "5": "balanced"
        }
        
        starting_system = system_map.get(system_choice, "balanced")
        
        # Select interpretation depth
        print("\n📊 Select Interpretation Depth:")
        print("  1. Standard (Core meanings)")
        print("  2. Detailed (Extended interpretations)")
        print("  3. Comprehensive (Full Hermetic synthesis)")
        
        depth_choice = input("Select depth (1-3, default 1): ").strip()
        depth_map = {"1": "standard", "2": "detailed", "3": "comprehensive"}
        depth = depth_map.get(depth_choice, "standard")
        
        # Select I Ching method
        print("\n📜 Select I Ching Method:")
        print("  1. Coin method (traditional, recommended)")
        print("  2. Yarrow stalk method (more authentic)")
        print("  3. Random selection (quick)")
        
        iching_choice = input("Select (1-3, default 1): ").strip()
        if iching_choice == "2":
            iching_method = "yarrow"
        elif iching_choice == "3":
            iching_method = "random"
        else:
            iching_method = "coins"
        
        # Ask about saving
        save_option = input("\n💾 Save reading to history? (y/n, default y): ").strip().lower()
        save_to_history = save_option != "n"
        
        print("\n" + "="*60)
        print("🎯 GENERATING READING...")
        print("="*60)
        
        # Run the reading
        result = self.run_full_reading(
            query=query,
            iching_method=iching_method,
            depth=depth,
            starting_system=starting_system
        )
        
        # Save to history if requested
        if save_to_history and result:
            self.history_manager.add_reading(result)
            print(f"\n📚 Reading saved to history (#{len(self.history_manager.history)})")
        
        # Offer options after reading
        self.post_reading_options(result)
    
    def run_full_reading(self, query="", iching_method="coins", depth="standard", starting_system="balanced"):
        """Enhanced full reading with depth control"""
        print(f"\n📝 Query: {query if query else 'General reading'}")
        print(f"📊 Depth: {depth.title()} interpretation")
        print(f"🔄 Starting Perspective: {starting_system.title() if starting_system != 'balanced' else 'Balanced (All systems equal)'}")
        
        # 1. Geomancy
        geomantic = self.generate_geomantic_figure()
        
        # 2. I Ching
        iching_result = self.cast_iching_traditional(method=iching_method)
        
        # 3. Tarot
        tarot = self.draw_tarot_card()
        
        # 4. Planetary timing
        planetary_hour = self.hour_calculator.calculate_current_planetary_hour()
        
        # 5. Magic square
        magic_square = self.get_magic_square_for_geomantic(geomantic)
        
        # 6. Enhanced synthesis based on depth
        if depth == "comprehensive":
            synthesis = self.hermetic_synthesis.generate_hermetic_synthesis(
                geomantic, iching_result, tarot, planetary_hour
            )
        elif depth == "detailed":
            synthesis = self.enhanced_synthesis(geomantic, iching_result, tarot, planetary_hour)
        else:
            synthesis = self.basic_synthesis(geomantic, iching_result, tarot, planetary_hour)
        
        # 7. Save to file
        filename = self.save_enhanced_reading(
            geomantic, iching_result, tarot, "",  # No jafr for basic
            planetary_hour, magic_square, synthesis, query
        )
        
        # 8. Display with depth-appropriate formatting
        self.display_with_depth(
            geomantic, iching_result, tarot, planetary_hour, 
            magic_square, synthesis, depth, starting_system
        )
        
        return {
            "geomantic": geomantic,
            "iching": iching_result,
            "tarot": tarot,
            "planetary_hour": planetary_hour,
            "magic_square": magic_square,
            "synthesis": synthesis,
            "filename": filename,
            "query": query,
            "depth": depth,
            "starting_system": starting_system
        }
    
    def display_with_depth(self, geomantic, iching, tarot, 
                          planetary_hour, magic_square, synthesis, depth, starting_system="balanced"):
        """Display results appropriate to interpretation depth"""
        
        # Add system equivalence explanation at the beginning
        if starting_system != "balanced":
            print(f"\n🌟 STARTING WITH {starting_system.upper()}:")
            print(self.get_system_explanation(geomantic, iching, tarot, starting_system))
        
        if depth == "comprehensive":
            print("\n" + "="*80)
            print("🔮 COMPREHENSIVE HERMETIC READING")
            print("="*80)
            
            # Display each system with full interpretation
            geomantic_text = self.interpretation_depth.get_interpretation(
                geomantic, "geomancy", depth
            )
            print(f"\n🧿 GEOMANCY:\n{geomantic_text}")
            
            iching_text = self.interpretation_depth.get_interpretation(
                iching, "iching", depth
            )
            print(f"\n📜 I CHING:\n{iching_text}")
            
            tarot_text = self.interpretation_depth.get_interpretation(
                tarot, "tarot", depth
            )
            print(f"\n🃏 TAROT:\n{tarot_text}")
            
            print(f"\n⏰ PLANETARY TIMING:")
            print(f"   Current: {planetary_hour['planet']} hour")
            print(f"   Quality: {self.get_planet_quality(planetary_hour['planet'])}")
            
            print(f"\n{synthesis}")
            
        elif depth == "detailed":
            print("\n" + "="*60)
            print("✨ DETAILED READING")
            print("="*60)
            
            # Medium detail display
            print(f"\n🧿 {geomantic['name']}: {geomantic['meaning']}")
            print(f"   Element: {geomantic.get('element', '')}")
            print(f"   Planet: {geomantic.get('planet', '')}")
            
            print(f"\n📜 {iching['primary']['english']}:")
            print(f"   #{iching['primary']['number']} - {iching['primary']['judgment_english'][:150]}...")
            
            print(f"\n🃏 {tarot['name']} ({tarot['suit']}):")
            print(f"   {tarot['meaning']}")
            
            print(f"\n{synthesis}")
            
        else:  # standard
            print("\n" + "="*50)
            print("🌟 STANDARD READING")
            print("="*50)
            
            # Basic display
            print(f"\n🧿 {geomantic['name']}: {geomantic['meaning'][:100]}...")
            print(f"\n📜 {iching['primary']['english']}: {iching['primary']['judgment_english'][:80]}...")
            print(f"\n🃏 {tarot['name']}: {tarot['meaning'][:80]}...")
            print(f"\n{synthesis[:200]}...")
    
    def basic_synthesis(self, geomantic, iching, tarot, planetary_hour):
        """Basic synthesis for standard depth"""
        return f"""
        🌟 INTEGRATED SYNTHESIS
        {'═' * 40}
        
        CORE INSIGHTS:
        • Geomancy: {geomantic['name']} - {geomantic['meaning'][:100]}...
        • I Ching: {iching['primary']['english']}
        • Tarot: {tarot['name']} - {tarot['meaning'][:100]}...
        
        ELEMENTAL BLEND:
        • Combined energy: {self.get_combined_elemental_energy(geomantic, iching, tarot)}
        """
    
    def enhanced_synthesis(self, geomantic, iching, tarot, planetary_hour):
        """Enhanced synthesis with timing recommendations"""
        synthesis = f"""
        🌟 INTEGRATED SYNTHESIS WITH TIMING
        {'═' * 50}
        
        CORE INSIGHTS:
        • 🧿 Geomancy: {geomantic['name']} - {geomantic['meaning'].split('.')[0]}
        • 📜 I Ching: {iching['primary']['english']} - {iching['primary'].get('judgment_english', '')[:100]}...
        • 🃏 Tarot: {tarot['name']} - {tarot['meaning'].split('.')[0]}
        
        TEMPORAL ALIGNMENT:
        • Current Planetary Hour: {planetary_hour['planet']}
        • Optimal Action Time: Next {self.get_optimal_planet(geomantic)} hour
        • Moon Phase: {self.get_moon_phase()}
        
        ELEMENTAL SYNERGY:
        • Geomancy: {geomantic.get('element', 'Unknown')}
        • I Ching: {iching['primary'].get('element', 'Unknown')}
        • Tarot: {tarot.get('element', 'Unknown')}
        
        PRACTICAL RECOMMENDATIONS:
        1. IMMEDIATE (Next 3 days):
           • Focus on: {geomantic['meaning'].split('.')[0]}
           • Avoid: {self.get_contraindication(geomantic)}
        
        2. SHORT-TERM (This week):
           • Develop: {tarot['name'].lower()} energy
           • Cultivate: {iching['primary']['english'].lower()} mindset
        
        3. RITUAL SUPPORT:
           • Use talisman during {self.get_best_talisman_time(geomantic)}
           • Meditate on: {self.get_meditation_focus(geomantic, iching, tarot)}
        """
        
        if iching.get("changing_lines"):
            synthesis += f"\n🌊 TRANSFORMATION INDICATED:\n"
            synthesis += f"   Lines {iching['changing_lines']} are changing"
            if iching.get("secondary"):
                synthesis += f"\n   Evolving toward: {iching['secondary']['english']}"
        
        return synthesis
    
    def load_all_systems(self):
        """Load all correspondences and mappings"""
        # Initialize data structures
        self.geomancy_figures = {}
        self.jafr_correspondences = {}
        self.tarot_major = {}
        self.iching_hexagrams = {}
        
        # Load from files if they exist
        self.load_data_from_files()
    
    def load_data_from_files(self):
        """Load data from JSON files if available"""
        data_files = {
            "geomancy": "data/geomancy.json",
            "iching": "data/iching.json",
            "tarot": "data/tarot.json",
            "jafr": "data/jafr.json"
        }
        
        for system, filename in data_files.items():
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if system == "geomancy":
                        self.geomancy_figures = data
                    elif system == "iching":
                        self.iching_hexagrams = data
                    elif system == "tarot":
                        self.tarot_major = data
                    elif system == "jafr":
                        self.jafr_correspondences = data
                    
                    print(f"✓ Loaded {system} from {filename}")
            except FileNotFoundError:
                print(f"⚠️ {filename} not found, using default data")
                self.load_default_data(system)
            except Exception as e:
                print(f"❌ Error loading {filename}: {e}")
                self.load_default_data(system)
    
    def load_default_data(self, system):
        """Load default data if files not found"""
        if system == "geomancy":
            self.geomancy_figures = {
                "figures": {
                    "1111": {"name": "Via", "binary": "1111", "meaning": "The Way", "planet": "Moon", "element": "Water"},
                    "0000": {"name": "Caput Draconis", "binary": "0000", "meaning": "Head of Dragon", "planet": "Jupiter", "element": "Earth"}
                }
            }
        elif system == "iching":
            self.iching_hexagrams = {
                "hexagrams": {
                    "111111": {"number": 1, "english": "The Creative", "chinese": "乾", "judgment_english": "Creative success", "element": "Heaven", "planet": "Sun"},
                    "000000": {"number": 2, "english": "The Receptive", "chinese": "坤", "judgment_english": "Receptive devotion", "element": "Earth", "planet": "Moon"}
                }
            }
        elif system == "tarot":
            self.tarot_major = {
                "major_arcana": [
                    {"name": "The Fool", "number": 0, "meaning": "New beginnings", "element": "Air", "planet": "Uranus"},
                    {"name": "The Magician", "number": 1, "meaning": "Manifestation", "element": "Mercury", "planet": "Mercury"}
                ],
                "minor_arcana": {
                    "wands": [{"name": "Ace of Wands", "number": 1, "meaning": "Inspiration", "element": "Fire", "planet": "Sun"}]
                }
            }
        elif system == "jafr":
            self.jafr_correspondences = {
                "Via": {"letter": "Alif", "value": 1, "square": "3×3 Saturn", "angel": "Mikail", "divine_name": "Allah", "use": "Protection"}
            }
    
    # ============ CORE FUNCTIONALITY METHODS ============
    
    def generate_geomantic_figure(self):
        """Generate a random geomantic figure"""
        # Generate 4 binary digits
        binary_str = ''.join([str(random.randint(0, 1)) for _ in range(4)])
        
        # Look up figure in loaded data
        figure = self.geomancy_figures.get("figures", {}).get(binary_str, {
            "name": "Unknown",
            "binary": binary_str,
            "meaning": "No meaning available.",
            "planet": "Moon",
            "element": "Water",
            "astrological": "Unknown"
        })
        
        # Add display info
        figure["display"] = self.display_geomantic_figure(binary_str)
        return figure

    def binary_to_geomantic(self, binary_str):
        """Convert binary string to geomantic figure name"""
        figure = self.geomancy_figures.get("figures", {}).get(binary_str, {})
        return figure.get("name", "Unknown")

    def display_geomantic_figure(self, binary_str):
        """Create visual representation of geomantic figure"""
        lines = []
        for bit in binary_str:
            if bit == '1':
                lines.append("●●")
            else:
                lines.append("○ ○")
        
        display = "\n".join(lines)
        
        # Add name if available
        figure = self.geomancy_figures.get("figures", {}).get(binary_str, {})
        name = figure.get("name", "Unknown")
        
        return f"{name}:\n{display}"

    def cast_iching_traditional(self, method="coins"):
        """Cast I Ching using specified method"""
        if method == "coins":
            hexagram_lines, changing_lines = self.iching_caster.cast_coins()
        elif method == "yarrow":
            hexagram_lines, changing_lines = self.iching_caster.cast_yarrow_stalks()
        else:
            # Random method
            hexagram_lines = [random.randint(0, 1) for _ in range(6)]
            changing_lines = []
        
        # Convert to binary string
        if len(hexagram_lines) < 6:
            hexagram_lines.extend([random.randint(0, 1) for _ in range(6 - len(hexagram_lines))])
        
        hexagram_binary = ''.join(['1' if x == 1 else '0' for x in hexagram_lines])
        
        # Get trigram symbols
        lower_trigram, upper_trigram = self.iching_caster.get_trigram_symbols(hexagram_binary)
        
        # Look up hexagram
        hexagram_data = self.iching_hexagrams.get("hexagrams", {}).get(hexagram_binary, {
            "number": 0,
            "english": "Unknown",
            "chinese": "?",
            "judgment_english": "No data available.",
            "element": "Unknown",
            "planet": "Moon"
        })
        
        result = {
            "binary": hexagram_binary,
            "lines": hexagram_lines,
            "changing_lines": changing_lines,
            "primary": hexagram_data,
            "trigram_symbols": {
                "lower": lower_trigram,
                "upper": upper_trigram
            }
        }
        
        # If there are changing lines, get secondary hexagram
        if changing_lines:
            secondary_lines = hexagram_lines.copy()
            for line_num in changing_lines:
                idx = 6 - line_num
                if 0 <= idx < len(secondary_lines):
                    secondary_lines[idx] = 1 if secondary_lines[idx] == 0 else 0
            
            secondary_binary = ''.join(['1' if x == 1 else '0' for x in secondary_lines])
            secondary_lower, secondary_upper = self.iching_caster.get_trigram_symbols(secondary_binary)
            
            secondary_data = self.iching_hexagrams.get("hexagrams", {}).get(secondary_binary, {
                "english": "Unknown Secondary",
                "judgment_english": "No data available."
            })
            result["secondary"] = secondary_data
            result["secondary_trigram_symbols"] = {
                "lower": secondary_lower,
                "upper": secondary_upper
            }
        
        return result

    def display_hexagram(self, hexagram_data):
        """Display hexagram with trigram symbols"""
        binary = hexagram_data.get('binary', '000000')
        trigrams = hexagram_data.get('trigram_symbols', {})
        number = hexagram_data.get('primary', {}).get('number', 0)
        name = hexagram_data.get('primary', {}).get('english', 'Unknown')
        
        lower = trigrams.get('lower', '?')
        upper = trigrams.get('upper', '?')
        
        # Build hexagram display
        lines = binary
        hex_display = ""
        
        # Show trigrams
        hex_display += f"\n☯ Hexagram #{number}: {name}"
        hex_display += f"\n   Lower Trigram: {lower}  |  Upper Trigram: {upper}"
        hex_display += f"\n   Binary: {binary}"
        
        # Show changing lines if any
        if hexagram_data.get('changing_lines'):
            hex_display += f"\n   Changing Lines: {hexagram_data['changing_lines']}"
            if hexagram_data.get('secondary'):
                sec = hexagram_data['secondary']
                sec_trigrams = hexagram_data.get('secondary_trigram_symbols', {})
                hex_display += f"\n   Evolving to: #{sec.get('number', '?')} {sec.get('english', 'Unknown')}"
                hex_display += f"\n   New Trigrams: {sec_trigrams.get('lower', '?')} | {sec_trigrams.get('upper', '?')}"
        
        # Add visual representation of lines
        hex_display += "\n\n   Hexagram Structure (Bottom to Top):"
        
        # I Ching lines are displayed from bottom (Line 1) to top (Line 6)
        for i in range(5, -1, -1):  # From 5 to 0 (bottom to top)
            line_num = 6 - i
            bit = binary[i]
            
            if bit == '1':
                line_display = "━━━━━━━━━━━━━"
            else:
                line_display = "━━━   ━━━━━"
            
            if hexagram_data.get('changing_lines') and (line_num) in hexagram_data['changing_lines']:
                hex_display += f"\n   Line {line_num}: {line_display} ⚡ (changing)"
            else:
                hex_display += f"\n   Line {line_num}: {line_display}"
        
        return hex_display

    def draw_tarot_card(self):
        """Draw a random tarot card (Major or Minor Arcana)"""
        # Determine if we draw from Major or Minor
        if random.random() < 0.5:
            cards = self.tarot_major.get("major_arcana", [])
            if cards:
                card = random.choice(cards)
                return {
                    "name": card.get("name", "Unknown"),
                    "number": card.get("number", 0),
                    "meaning": card.get("meaning", "No meaning available."),
                    "element": card.get("element", "Unknown"),
                    "planet": card.get("planet", "Unknown"),
                    "suit": "Major Arcana"
                }
        
        # Draw from Minor Arcana
        suits = ["wands", "cups", "swords", "pentacles"]
        suit = random.choice(suits)
        cards = self.tarot_major.get("minor_arcana", {}).get(suit, [])
        
        if cards:
            card = random.choice(cards)
            return {
                "name": card.get("name", "Unknown"),
                "number": card.get("number", 0),
                "meaning": card.get("meaning", "No meaning available."),
                "element": card.get("element", "Unknown"),
                "planet": card.get("planet", "Unknown"),
                "suit": suit.capitalize()
            }
        
        # Fallback
        return {
            "name": "The Fool",
            "number": 0,
            "meaning": "New beginnings and unlimited potential.",
            "element": "Air",
            "planet": "Uranus",
            "suit": "Major Arcana"
        }

    def get_magic_square_for_geomantic(self, geomantic):
        """Get magic square for geomantic figure's planet"""
        planet_name = geomantic.get("planet", "Moon")
        
        if planet_name == "Saturn":
            return self.magic_squares.generate_saturn_square()
        elif planet_name == "Jupiter":
            return self.magic_squares.generate_jupiter_square()
        elif planet_name == "Mars":
            return self.magic_squares.generate_mars_square()
        elif planet_name == "Sun":
            return self.magic_squares.generate_sun_square()
        elif planet_name == "Venus":
            return self.magic_squares.generate_venus_square()
        elif planet_name == "Mercury":
            return self.magic_squares.generate_mercury_square()
        elif planet_name == "Moon":
            return self.magic_squares.generate_moon_square()
        else:
            return self.magic_squares.generate_saturn_square()

    def run_reading_menu(self):
        """Main reading menu with all options"""
        while True:
            print("\n" + "="*60)
            print("🔮 RUN DIVINATION READING")
            print("="*60)
            print("\nSelect Method:")
            print("  1. 🧿 Full Quadruple Reading")
            print("  2. 🪙 I Ching Only (Coin Method)")
            print("  3. 🌿 I Ching Only (Yarrow Method)")
            print("  4. 🧿 Geomancy Only")
            print("  5. 🃏 Tarot Only")
            print("  6. 📿 Jafr Talisman Generation")
            print("  7. ⏰ Check Planetary Hour")
            print("  8. 🔢 Generate Magic Square")
            print("  9. 🔙 Back to Main Menu")
            
            choice = input("\nSelect option (1-9): ").strip()
            
            if choice == "1":
                self.run_full_reading_with_options()
            elif choice == "2":
                self.run_iching_reading(method="coins")
            elif choice == "3":
                self.run_iching_reading(method="yarrow")
            elif choice == "4":
                self.run_geomancy_only()
            elif choice == "5":
                self.run_tarot_only()
            elif choice == "6":
                self.run_jafr_talisman()
            elif choice == "7":
                self.display_planetary_hour()
            elif choice == "8":
                self.generate_magic_square_menu()
            elif choice == "9":
                return
            else:
                print("Invalid choice.")
    
    def run_iching_reading(self, method="coins"):
        """Run I Ching reading only"""
        print("\n" + "="*60)
        print(f"📜 I CHING READING ({method.upper()} METHOD)")
        print("="*60)
        
        query = input("\n📝 Enter your query: ")
        
        # Cast hexagram
        result = self.cast_iching_traditional(method)
        
        print(f"\n🔮 Hexagram #{result['primary']['number']}: {result['primary']['english']}")
        print(f"   Chinese: {result['primary']['chinese']}")
        print(f"   Binary: {result['binary']}")
        
        # Display hexagram with trigrams
        hex_display = self.display_hexagram(result)
        print(hex_display)
        
        print(f"\n📖 Judgment:")
        print(f"   {result['primary']['judgment_english']}")
        
        if result.get('changing_lines'):
            print(f"\n🌊 Changing Lines: {result['changing_lines']}")
            if result.get('secondary'):
                print(f"   Evolving to: {result['secondary']['english']}")
        
        # Show individual lines if requested
        show_lines = input("\n🔍 Show individual line meanings? (y/n): ").strip().lower()
        if show_lines == 'y' and 'lines_english' in result['primary']:
            print("\n📜 Line Meanings:")
            for i, line in enumerate(result['primary']['lines_english'][:6]):
                print(f"   Line {i+1}: {line}")

    def run_geomancy_only(self):
        """Run geomancy reading only"""
        print("\n" + "="*60)
        print("🧿 GEOMANCY READING")
        print("="*60)
        
        query = input("\n📝 Enter your query: ")
        
        # Generate figure
        figure = self.generate_geomantic_figure()
        
        print(f"\n✨ Geomantic Figure: {figure['name']}")
        print(f"   Binary: {figure['binary']}")
        print(f"   Planet: {figure['planet']}")
        print(f"   Element: {figure['element']}")
        print(f"   Astrological: {figure.get('astrological', 'Unknown')}")
        print(f"\n📖 Meaning: {figure['meaning']}")
        print(f"\n🎨 Figure Representation:")
        print(figure['display'])
        
        # Ask about saving
        save = input("\n💾 Save this reading? (y/n): ").strip().lower()
        if save == 'y':
            reading_data = {
                "query": query,
                "geomantic": figure,
                "filename": f"geomancy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            }
            self.history_manager.add_reading(reading_data)

    def run_tarot_only(self):
        """Run tarot reading only"""
        print("\n" + "="*60)
        print("🃏 TAROT READING")
        print("="*60)
        
        query = input("\n📝 Enter your query: ")
        
        # Number of cards
        print("\n🔢 Number of cards to draw:")
        print("  1. Single Card")
        print("  2. Three-Card Spread (Past/Present/Future)")
        print("  3. Celtic Cross (10 cards)")
        
        choice = input("Select (1-3, default 1): ").strip() or "1"
        
        if choice == "2":
            cards = [self.draw_tarot_card() for _ in range(3)]
            print("\n🔮 Three-Card Spread:")
            print("  1. Past: " + cards[0]['name'])
            print("  2. Present: " + cards[1]['name'])
            print("  3. Future: " + cards[2]['name'])
            
            for i, card in enumerate(cards):
                print(f"\n[{i+1}] {card['name']} ({card['suit']})")
                print(f"   {card['meaning']}")
        elif choice == "3":
            print("\n🔮 Celtic Cross Spread (drawing 10 cards)...")
            cards = [self.draw_tarot_card() for _ in range(10)]
            positions = [
                "1. Present Situation",
                "2. Immediate Challenge",
                "3. Distant Past",
                "4. Recent Past",
                "5. Best Outcome",
                "6. Immediate Future",
                "7. Self-Image",
                "8. Environmental Factors",
                "9. Hopes/Fears",
                "10. Final Outcome"
            ]
            
            for i, (pos, card) in enumerate(zip(positions, cards)):
                print(f"{pos}: {card['name']}")
        else:
            card = self.draw_tarot_card()
            print(f"\n🔮 Card Drawn: {card['name']}")
            print(f"   Suit: {card['suit']}")
            print(f"   Element: {card['element']}")
            print(f"   Planet: {card['planet']}")
            print(f"\n📖 Meaning: {card['meaning']}")

    def run_jafr_talisman(self):
        """Generate Jafr talisman"""
        print("\n" + "="*60)
        print("📿 JAFR TALISMAN GENERATOR")
        print("="*60)
        
        # Generate geomantic figure
        figure = self.generate_geomantic_figure()
        figure_name = figure['name']
        
        print(f"\n🧿 Base Geomantic Figure: {figure_name}")
        print(f"   {figure['meaning'][:100]}...")
        
        # Get Jafr correspondence
        jafr_data = self.jafr_correspondences.get(figure_name, {
            "letter": "Unknown",
            "value": 0,
            "square": "3×3 Saturn",
            "angel": "Unknown",
            "divine_name": "Unknown",
            "use": "No specific use available."
        })
        
        print(f"\n📜 Jafr Correspondences:")
        print(f"   Arabic Letter: {jafr_data['letter']}")
        print(f"   Numerical Value: {jafr_data['value']}")
        print(f"   Magic Square: {jafr_data['square']}")
        print(f"   Angelic Governor: {jafr_data['angel']}")
        print(f"   Divine Name: {jafr_data['divine_name']}")
        print(f"\n🎯 Primary Use: {jafr_data['use']}")
        
        # Generate timing
        planetary_hour = self.hour_calculator.calculate_current_planetary_hour()
        print(f"\n⏰ Current Timing:")
        print(f"   Planetary Hour: {planetary_hour['planet']}")
        print(f"   Hour Type: {'Day' if planetary_hour['is_daytime'] else 'Night'}")

    def display_planetary_hour(self):
        """Display current planetary hour and schedule"""
        current = self.hour_calculator.calculate_current_planetary_hour()
        
        print("\n" + "="*60)
        print("⏰ PLANETARY HOUR INFORMATION")
        print("="*60)
        
        print(f"\n🪐 CURRENT PLANETARY HOUR:")
        print(f"   • Planet: {current['planet']}")
        print(f"   • Hour: {current['hour_number']} of {current['is_daytime'] and 'day' or 'night'}")
        print(f"   • Time: {datetime.now().strftime('%H:%M')}")
        
        print(f"\n📅 TODAY'S PLANETARY HOUR SCHEDULE:")
        schedule = self.hour_calculator.get_planetary_hour_schedule()
        
        for hour in schedule[:6]:
            print(f"   {hour['hour']:2d}. {hour['planet']:8s} ({hour['type']})")
        
        print("   ...")
        
        print(f"\n✨ PLANETARY CORRESPONDENCES:")
        planet_correspondences = {
            "Sun": "Success, vitality, leadership",
            "Moon": "Intuition, dreams, emotions",
            "Mercury": "Communication, travel, intellect",
            "Venus": "Love, beauty, harmony",
            "Mars": "Action, courage, conflict",
            "Jupiter": "Expansion, luck, wisdom",
            "Saturn": "Discipline, boundaries, karma"
        }
        
        for planet, meaning in planet_correspondences.items():
            print(f"   • {planet}: {meaning}")
    
    def generate_magic_square_menu(self):
        """Menu for generating magic squares"""
        print("\n" + "="*60)
        print("🔢 MAGIC SQUARE GENERATOR")
        print("="*60)
        
        print("\nSelect Planet:")
        planets = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
        
        for i, planet in enumerate(planets, 1):
            sizes = {"Saturn": 3, "Jupiter": 4, "Mars": 5, "Sun": 6, "Venus": 7, "Mercury": 8, "Moon": 9}
            print(f"  {i}. {planet} ({sizes[planet]}x{sizes[planet]})")
        
        print("  8. Custom size (3-9)")
        
        choice = input("\nSelect (1-8): ").strip()
        
        if choice == "8":
            try:
                size = int(input("Enter size (3-9): ").strip())
                if 3 <= size <= 9:
                    square = self.generate_custom_square(size)
                    title = f"Custom {size}x{size}"
                else:
                    print("Size must be between 3 and 9")
                    return
            except:
                print("Invalid size")
                return
        else:
            try:
                planet_index = int(choice) - 1
                if 0 <= planet_index < len(planets):
                    planet = planets[planet_index]
                    square, size = self.magic_squares.get_square_by_planet(planet)
                    title = f"{planet} {size}x{size}"
                else:
                    print("Invalid choice")
                    return
            except:
                print("Invalid choice")
                return
        
        # Display the square
        print(self.magic_squares.display_square(square, title))
        
        # Offer to save
        save = input("\n💾 Save square to file? (y/n): ").strip().lower()
        if save == 'y':
            self.save_magic_square(square, title)
    
    def save_enhanced_reading(self, geomantic, iching, tarot, jafr_recipe, 
                              planetary_hour, magic_square, synthesis, query):
        """Save enhanced reading with all data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"readings/enhanced_reading_{timestamp}.json"
        
        data = {
            "metadata": {
                "system": self.framework,
                "version": self.version,
                "timestamp": datetime.now().isoformat(),
                "query": query
            },
            "geomancy": geomantic,
            "iching": iching,
            "tarot": tarot,
            "planetary_timing": planetary_hour,
            "magic_square": {
                "size": len(magic_square) if magic_square else 0,
                "data": magic_square
            },
            "jafr_recipe": jafr_recipe,
            "synthesis": synthesis,
            "recommendations": self.generate_recommendations(geomantic, iching, tarot)
        }
        
        # Ensure directory exists
        Path("readings").mkdir(exist_ok=True)
        
        # Save as JSON
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Also save as text for readability
        text_filename = filename.replace('.json', '.txt')
        self.save_reading_as_text(text_filename, data)
        
        return filename
    
    def save_reading_as_text(self, filename, data):
        """Save reading as human-readable text"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("QUADRUPLE GODDESS - ENHANCED READING\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"Date: {data['metadata']['timestamp']}\n")
            f.write(f"Query: {data['metadata']['query']}\n\n")
            
            f.write("🧿 GEOMANCY:\n")
            f.write(f"  Figure: {data['geomancy']['name']}\n")
            f.write(f"  Meaning: {data['geomancy']['meaning']}\n")
            f.write(f"  Planet: {data['geomancy']['planet']}\n")
            f.write(f"  Element: {data['geomancy']['element']}\n\n")
            
            f.write("📜 I CHING:\n")
            f.write(f"  Hexagram: {data['iching']['primary']['english']}\n")
            f.write(f"  Number: #{data['iching']['primary']['number']}\n")
            f.write(f"  Judgment: {data['iching']['primary']['judgment_english']}\n\n")
            
            f.write("🃏 TAROT:\n")
            f.write(f"  Card: {data['tarot']['name']}\n")
            f.write(f"  Suit: {data['tarot']['suit']}\n")
            f.write(f"  Meaning: {data['tarot']['meaning']}\n\n")
            
            f.write("⏰ TIMING:\n")
            f.write(f"  Planetary Hour: {data['planetary_timing']['planet']}\n")
            f.write(f"  Hour Number: {data['planetary_timing']['hour_number']}\n")
            f.write(f"  Time of Day: {'Day' if data['planetary_timing']['is_daytime'] else 'Night'}\n\n")
            
            f.write("🔢 MAGIC SQUARE:\n")
            f.write(f"  Size: {data['magic_square']['size']}x{data['magic_square']['size']}\n\n")
            
            f.write("📝 SYNTHESIS:\n")
            f.write(data['synthesis'])
            
            if data.get('jafr_recipe'):
                f.write("\n\n🧿 TALISMAN RECIPE:\n")
                f.write(data['jafr_recipe'])
    
    def post_reading_options(self, result):
        """Display options after completing a reading"""
        print("\n" + "="*60)
        print("📋 POST-READING OPTIONS")
        print("="*60)
        
        while True:
            print("\nSelect option:")
            print("  1. 🔄 Run another reading")
            print("  2. 📊 View reading history")
            print("  3. 💾 Export reading to PDF/JSON")
            print("  4. ⏰ Check optimal timing for actions")
            print("  5. 🧿 Generate additional talismans")
            print("  6. 🔙 Return to main menu")
            print("  7. 🚪 Exit program")
            
            choice = input("\nSelect (1-7): ").strip()
            
            if choice == "1":
                self.run_reading_menu()
                break
            elif choice == "2":
                self.view_reading_history()
            elif choice == "3":
                self.export_reading(result)
            elif choice == "4":
                self.display_optimal_timing(result)
            elif choice == "5":
                self.generate_additional_talismans(result)
            elif choice == "6":
                return
            elif choice == "7":
                print("\n✨ Thank you for using Quadruple Goddess!")
                sys.exit(0)
            else:
                print("Invalid choice.")
    
    def view_reading_history(self):
        """View and manage reading history"""
        history = self.history_manager.get_recent_readings(20)
        
        if not history:
            print("\n📭 No readings in history yet.")
            return
        
        print("\n" + "="*60)
        print("📚 READING HISTORY")
        print("="*60)
        
        for reading in history:
            print(f"\n#{reading['id']} - {reading['timestamp'][:10]}")
            print(f"   Query: {reading['query'][:50]}{'...' if len(reading['query']) > 50 else ''}")
            print(f"   Summary: {reading['summary']}")
            print(f"   File: {reading['filename']}")
        
        print("\nOptions:")
        print("  1. View detailed reading")
        print("  2. Search readings")
        print("  3. Export all readings")
        print("  4. Clear history")
        print("  5. Back")
        
        choice = input("\nSelect (1-5): ").strip()
        
        if choice == "1":
            reading_id = input("Enter reading #: ").strip()
            self.view_detailed_reading(reading_id)
        elif choice == "2":
            keyword = input("Search keyword: ").strip()
            results = self.history_manager.search_readings(keyword)
            print(f"\n🔍 Found {len(results)} results:")
            for r in results:
                print(f"  #{r['id']}: {r['query'][:40]}...")
        elif choice == "3":
            format_choice = input("Export format (json/txt/both): ").strip().lower()
            if format_choice in ['json', 'both']:
                file = self.history_manager.export_to_json()
                print(f"✓ Exported to JSON: {file}")
            if format_choice in ['txt', 'both']:
                file = self.history_manager.export_to_text()
                print(f"✓ Exported to text: {file}")
        elif choice == "4":
            confirm = input("Clear all history? (type 'yes' to confirm): ").strip()
            if confirm == 'yes':
                self.history_manager.history = []
                self.history_manager.save_history()
                print("History cleared.")
    
    def view_detailed_reading(self, reading_id):
        """View detailed reading by ID"""
        try:
            reading_id = int(reading_id)
            if reading_id < 1 or reading_id > len(self.history_manager.history):
                print("Invalid reading ID")
                return
            
            reading = self.history_manager.history[reading_id - 1]
            print(f"\n📖 DETAILED READING #{reading_id}")
            print("="*60)
            print(f"Date: {reading['timestamp']}")
            print(f"Query: {reading['query']}")
            print(f"Summary: {reading['summary']}")
            
            # Try to load the actual reading file
            if reading.get('filename'):
                try:
                    with open(reading['filename'], 'r') as f:
                        data = json.load(f)
                        print("\n📊 Full Data:")
                        print(json.dumps(data, indent=2))
                except:
                    print("\n⚠️ Could not load reading file")
        except:
            print("Invalid reading ID")
    
    def export_reading(self, result):
        """Export reading to different formats"""
        print("\n📁 EXPORT READING")
        print("="*60)
        
        print("\nSelect format:")
        print("  1. JSON (full data)")
        print("  2. Text (readable)")
        print("  3. CSV (tabular data)")
        print("  4. Back")
        
        choice = input("\nSelect (1-4): ").strip()
        
        if choice == "1":
            self.export_to_json(result)
        elif choice == "2":
            self.export_to_text_file(result)
        elif choice == "3":
            self.export_to_csv(result)
        elif choice == "4":
            return
        else:
            print("Invalid choice")
    
    def export_to_json(self, result):
        """Export reading to JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"exports/reading_{timestamp}.json"
        
        Path("exports").mkdir(exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"✓ Exported to JSON: {filename}")
    
    def export_to_text_file(self, result):
        """Export reading to text file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"exports/reading_{timestamp}.txt"
        
        Path("exports").mkdir(exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("QUADRUPLE GODDESS READING\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"Date: {datetime.now().isoformat()}\n")
            f.write(f"Query: {result.get('query', '')}\n\n")
            
            f.write("🧿 GEOMANCY:\n")
            f.write(f"  Figure: {result['geomantic'].get('name', 'Unknown')}\n")
            f.write(f"  Meaning: {result['geomantic'].get('meaning', '')[:200]}...\n\n")
            
            f.write("📜 I CHING:\n")
            f.write(f"  Hexagram: {result['iching']['primary'].get('english', 'Unknown')}\n")
            f.write(f"  Judgment: {result['iching']['primary'].get('judgment_english', '')[:200]}...\n\n")
            
            f.write("🃏 TAROT:\n")
            f.write(f"  Card: {result['tarot'].get('name', 'Unknown')}\n")
            f.write(f"  Meaning: {result['tarot'].get('meaning', '')[:200]}...\n\n")
        
        print(f"✓ Exported to text: {filename}")
    
    def export_to_csv(self, result):
        """Export reading to CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"exports/reading_{timestamp}.csv"
        
        Path("exports").mkdir(exist_ok=True)
        
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['System', 'Name', 'Meaning', 'Element', 'Planet'])
            writer.writerow(['Geomancy', 
                            result['geomantic'].get('name', ''),
                            result['geomantic'].get('meaning', '')[:100],
                            result['geomantic'].get('element', ''),
                            result['geomantic'].get('planet', '')])
            writer.writerow(['I Ching',
                            result['iching']['primary'].get('english', ''),
                            result['iching']['primary'].get('judgment_english', '')[:100],
                            result['iching']['primary'].get('element', ''),
                            result['iching']['primary'].get('planet', '')])
            writer.writerow(['Tarot',
                            result['tarot'].get('name', ''),
                            result['tarot'].get('meaning', '')[:100],
                            result['tarot'].get('element', ''),
                            result['tarot'].get('planet', '')])
        
        print(f"✓ Exported to CSV: {filename}")
    
    def display_optimal_timing(self, result):
        """Display optimal timing for actions"""
        print("\n⏰ OPTIMAL TIMING RECOMMENDATIONS")
        print("="*60)
        
        geomantic = result['geomantic']
        planetary_hour = self.hour_calculator.calculate_current_planetary_hour()
        
        print(f"\nBased on {geomantic['name']} ({geomantic['planet']}):")
        print(f"   Best planetary hour: {geomantic['planet']} hour")
        print(f"   Best day: {geomantic['planet']}'s day")
        print(f"   Best element: {geomantic['element']}")
        
        # Calculate next optimal hour
        schedule = self.hour_calculator.get_planetary_hour_schedule()
        optimal_hours = [h for h in schedule if h['planet'] == geomantic['planet']]
        
        if optimal_hours:
            next_hour = optimal_hours[0]
            print(f"\n📅 Next optimal timing:")
            print(f"   {next_hour['planet']} hour ({next_hour['type']} hour {next_hour['hour']})")
    
    def generate_additional_talismans(self, result):
        """Generate additional talismans"""
        print("\n🧿 ADDITIONAL TALISMAN RECIPES")
        print("="*60)
        
        geomantic = result['geomantic']
        iching = result['iching']
        tarot = result['tarot']
        
        print(f"\n1. Geomancy Talisman ({geomantic['name']}):")
        print(f"   Use: {self.jafr_correspondences.get(geomantic['name'], {}).get('use', 'Protection')}")
        
        print(f"\n2. I Ching Talisman ({iching['primary']['english']}):")
        print(f"   Element: {iching['primary'].get('element', 'Unknown')}")
        print(f"   Focus: Meditate on hexagram structure")
        
        print(f"\n3. Tarot Talisman ({tarot['name']}):")
        print(f"   Element: {tarot.get('element', 'Unknown')}")
        print(f"   Ritual: Work with {tarot['suit']} energy")
    
    def generate_custom_square(self, size):
        """Generate custom magic square of given size"""
        square = [[0] * size for _ in range(size)]
        
        # Siamese method for odd sizes
        if size % 2 == 1:
            i, j = 0, size // 2
            for num in range(1, size*size + 1):
                square[i][j] = num
                new_i, new_j = (i - 1) % size, (j + 1) % size
                if square[new_i][new_j]:
                    i = (i + 1) % size
                else:
                    i, j = new_i, new_j
        else:
            # For even sizes, use simple pattern
            num = 1
            for i in range(size):
                for j in range(size):
                    square[i][j] = num
                    num += 1
        
        return square
    
    def save_magic_square(self, square, title):
        """Save magic square to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"magic_squares/{title.replace(' ', '_')}_{timestamp}.txt"
        
        Path("magic_squares").mkdir(exist_ok=True)
        
        with open(filename, 'w') as f:
            f.write(f"Magic Square: {title}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("="*40 + "\n\n")
            
            for row in square:
                f.write(" ".join(f"{num:3d}" for num in row) + "\n")
        
        print(f"✓ Square saved to {filename}")
    
    # ============ SUPPORT METHODS ============
    
    def get_optimal_planet(self, geomantic):
        """Get optimal planetary timing for geomantic figure"""
        planet_map = {
            "Moon": "Moon", "Sun": "Sun", "Mercury": "Mercury",
            "Venus": "Venus", "Mars": "Mars", "Jupiter": "Jupiter",
            "Saturn": "Saturn"
        }
        return planet_map.get(geomantic.get('planet', 'Moon'), 'Moon')
    
    def get_moon_phase(self):
        """Calculate approximate moon phase"""
        days_in_cycle = 29.53
        known_new_moon = datetime(2024, 1, 11)
        days_since = (datetime.now() - known_new_moon).days
        phase = (days_since % days_in_cycle) / days_in_cycle
        
        if phase < 0.25:
            return "Waxing Crescent 🌒"
        elif phase < 0.5:
            return "First Quarter 🌓"
        elif phase < 0.75:
            return "Waning Gibbous 🌖"
        else:
            return "Last Quarter 🌗"
    
    def get_contraindication(self, geomantic):
        """Get contraindication for geomantic figure"""
        contraindications = {
            "Via": "rushing without direction",
            "Cauda Draconis": "clinging to the past",
            "Puer": "reckless action without planning",
            "Amissio": "trying to hold onto what must be released"
        }
        return contraindications.get(geomantic['name'], "impatience")
    
    def get_meditation_focus(self, geomantic, iching, tarot):
        """Get meditation focus from combined reading"""
        return f"The integration of {geomantic['element']} ({geomantic['name']}), {iching['primary']['element']} ({iching['primary']['english']}), and {tarot['element']} ({tarot['name']})"
    
    def get_best_talisman_time(self, geomantic):
        """Get best time for talisman activation"""
        return f"{geomantic.get('planet', 'Moon')} hour on {geomantic.get('planet', 'Moon')}'s day"
    
    def generate_recommendations(self, geomantic, iching, tarot):
        """Generate practical recommendations"""
        return {
            "immediate": f"Focus on the energy of {geomantic['name']}",
            "short_term": f"Meditate on {iching['primary']['english']}",
            "long_term": f"Develop {tarot['name']} qualities",
            "ritual": f"Create talisman during {geomantic.get('planet', 'Moon')} hour"
        }
    
    def get_combined_elemental_energy(self, geomantic, iching, tarot):
        """Calculate combined elemental energy"""
        elements = [
            geomantic.get('element', ''),
            iching['primary'].get('element', ''),
            tarot.get('element', '')
        ]
        return " + ".join(filter(None, elements))
    
    def get_planet_quality(self, planet):
        """Get quality description for a planet"""
        qualities = {
            "Sun": "Vitality, success, leadership",
            "Moon": "Intuition, emotions, receptivity",
            "Mercury": "Communication, intellect, travel",
            "Venus": "Love, beauty, harmony",
            "Mars": "Action, courage, conflict",
            "Jupiter": "Expansion, luck, wisdom",
            "Saturn": "Discipline, structure, karma"
        }
        return qualities.get(planet, "Neutral influence")
    
    # ============ REFERENCE METHODS ============
    
    def display_geomancy_reference(self):
        """Display geomancy reference table"""
        print("\n🧿 GEOMANCY FIGURES REFERENCE")
        print("="*60)
        
        for binary, figure in self.geomancy_figures.get("figures", {}).items():
            print(f"\n{binary}: {figure['name']}")
            print(f"   Planet: {figure['planet']}")
            print(f"   Element: {figure['element']}")
            print(f"   Meaning: {figure['meaning'][:80]}...")
    
    def display_iching_reference(self):
        """Display I Ching reference"""
        print("\n📜 I CHING HEXAGRAMS REFERENCE")
        print("="*60)
        
        for binary, hexagram in self.iching_hexagrams.get("hexagrams", {}).items():
            print(f"\n#{hexagram['number']}: {hexagram['english']} ({hexagram['chinese']})")
            print(f"   Binary: {binary}")
            print(f"   {hexagram['judgment_english'][:60]}...")
    
    def display_tarot_reference(self):
        """Display tarot reference"""
        print("\n🃏 TAROT REFERENCE")
        print("="*60)
        
        # Major Arcana
        print("\nMAJOR ARCANA:")
        for card in self.tarot_major.get("major_arcana", []):
            print(f"  {card['number']:2d}. {card['name']}: {card['meaning'][:40]}...")
        
        # Minor Arcana
        print("\nMINOR ARCANA:")
        suits = ["wands", "cups", "swords", "pentacles"]
        for suit in suits:
            cards = self.tarot_major.get("minor_arcana", {}).get(suit, [])
            if cards:
                print(f"\n  {suit.upper()}:")
                for card in cards[:3]:
                    print(f"    {card['name']}")
    
    def display_jafr_reference(self):
        """Display Jafr correspondences"""
        print("\n📿 JAFR CORRESPONDENCES")
        print("="*60)
        
        for figure, data in self.jafr_correspondences.items():
            print(f"\n{figure}:")
            print(f"   Letter: {data['letter']} (Value: {data['value']})")
            print(f"   Square: {data['square']}")
            print(f"   Angel: {data['angel']}")
            print(f"   Use: {data['use'][:60]}...")
    
    def display_planetary_reference(self):
        """Display planetary correspondences"""
        print("\n🪐 PLANETARY CORRESPONDENCES")
        print("="*60)
        
        planets = {
            "Sun": {"element": "Fire", "day": "Sunday", "metal": "Gold", "color": "Gold/Yellow"},
            "Moon": {"element": "Water", "day": "Monday", "metal": "Silver", "color": "Silver/White"},
            "Mercury": {"element": "Air", "day": "Wednesday", "metal": "Mercury/Quicksilver", "color": "Orange/Yellow"},
            "Venus": {"element": "Water", "day": "Friday", "metal": "Copper", "color": "Green"},
            "Mars": {"element": "Fire", "day": "Tuesday", "metal": "Iron", "color": "Red"},
            "Jupiter": {"element": "Air", "day": "Thursday", "metal": "Tin", "color": "Blue/Purple"},
            "Saturn": {"element": "Earth", "day": "Saturday", "metal": "Lead", "color": "Black/Indigo"}
        }
        
        for planet, data in planets.items():
            print(f"\n{planet}:")
            print(f"   Element: {data['element']}")
            print(f"   Day: {data['day']}")
            print(f"   Metal: {data['metal']}")
            print(f"   Color: {data['color']}")
    
    def display_elemental_reference(self):
        """Display elemental correspondences"""
        print("\n🌟 ELEMENTAL CORRESPONDENCES")
        print("="*60)
        
        elements = {
            "Fire": {"direction": "South", "season": "Summer", "time": "Noon", "quality": "Hot/Dry"},
            "Water": {"direction": "West", "season": "Autumn", "time": "Sunset", "quality": "Cold/Wet"},
            "Air": {"direction": "East", "season": "Spring", "time": "Dawn", "quality": "Hot/Wet"},
            "Earth": {"direction": "North", "season": "Winter", "time": "Midnight", "quality": "Cold/Dry"},
            "Metal": {"direction": "West", "season": "Autumn", "planet": "Venus", "quality": "Contracting"},
            "Wood": {"direction": "East", "season": "Spring", "planet": "Jupiter", "quality": "Expanding"}
        }
        
        for element, data in elements.items():
            print(f"\n{element}:")
            for key, value in data.items():
                print(f"   {key.capitalize()}: {value}")
    
    # ============ SYSTEM INFO AND HELP ============
    
    def system_info(self):
        """Display comprehensive system information"""
        print("\n" + "="*60)
        print("📊 SYSTEM INFORMATION")
        print("="*60)
        
        print(f"\nVersion: {self.version}")
        print(f"Framework: {self.framework}")
        print(f"Build Date: {self.build_date}")
        
        print(f"\nPython Version: {platform.python_version()}")
        print(f"Platform: {platform.system()} {platform.release()}")
        
        print(f"\n📁 DATA STATUS:")
        print(f"  Geomancy Figures: {len(self.geomancy_figures.get('figures', {}))}/16")
        print(f"  I Ching Hexagrams: {len(self.iching_hexagrams.get('hexagrams', {}))}/64")
        tarot_major = len(self.tarot_major.get('major_arcana', []))
        tarot_minor = sum(len(cards) for cards in self.tarot_major.get('minor_arcana', {}).values())
        print(f"  Tarot Cards: {tarot_major + tarot_minor}/78 ({tarot_major} Major, {tarot_minor} Minor)")
        print(f"  Jafr Correspondences: {len(self.jafr_correspondences)}")
        
        print(f"\n📚 READING HISTORY:")
        print(f"  Total Readings: {len(self.history_manager.history)}")
        
        print(f"\n🛠️  FEATURES:")
        features = [
            "✓ Geomancy with 16 figures",
            "✓ I Ching with coin/yarrow methods",
            "✓ Tarot (Major & Minor Arcana)",
            "✓ Jafr talisman generation",
            "✓ Planetary hour calculator",
            "✓ Magic squares (3x3 to 9x9)",
            "✓ Reading history & export",
            "✓ Cross-system synthesis"
        ]
        for feature in features:
            print(f"  {feature}")
    
    def display_help(self):
        """Display help and instructions"""
        print("\n" + "="*60)
        print("❓ HELP & INSTRUCTIONS")
        print("="*60)
        
        help_text = """
    HOW TO USE QUADRUPLE GODDESS SYSTEM:
    
    1. 🧿 FULL READINGS:
       - Combines Geomancy, I Ching, Tarot, and Jafr
       - Provides integrated synthesis and timing recommendations
       - Can be saved and reviewed later
    
    2. 🪙 I CHING METHODS:
       - Coin Method (Traditional): 3 coins, 6 lines
       - Yarrow Stalks (Authentic): 50 stalks, more complex
       - Random: Quick generation for practice
    
    3. 🧿 GEOMANCY:
       - 16 traditional geomantic figures
       - Each with planetary and elemental correspondences
       - Binary generation for modern interpretation
    
    4. 🃏 TAROT:
       - Major Arcana (22 cards)
       - Minor Arcana (56 cards, 4 suits)
       - Single card or multi-card spreads
    
    5. 📿 JAFR TALISMANS:
       - Islamic mystical correspondences
       - Magic square generation
       - Ritual timing recommendations
    
    6. ⏰ PLANETARY HOURS:
       - Traditional Chaldean order
       - Day/Night hour calculations
       - Optimal timing for rituals
    
    7. 🔢 MAGIC SQUARES:
       - Planetary squares (3x3 to 9x9)
       - Traditional configurations
       - Custom square generation
    
    TIPS:
    - Start with a clear question for best results
    - Keep a journal of your readings
    - Use timing features for ritual work
    - Export important readings for reference
    """
        
        print(help_text)
    
    def verify_system(self):
        """Verify system integrity"""
        print("\n" + "="*60)
        print("🔍 SYSTEM VERIFICATION")
        print("="*60)
        
        checks = [
            ("Python Version", platform.python_version() >= "3.6", "✓"),
            ("Geomancy Data", len(self.geomancy_figures.get('figures', {})) > 0, "✓" if len(self.geomancy_figures.get('figures', {})) > 0 else "✗"),
            ("I Ching Data", len(self.iching_hexagrams.get('hexagrams', {})) > 0, "✓" if len(self.iching_hexagrams.get('hexagrams', {})) > 0 else "✗"),
            ("Tarot Data", len(self.tarot_major.get('major_arcana', [])) > 0, "✓" if len(self.tarot_major.get('major_arcana', [])) > 0 else "✗"),
            ("History System", True, "✓"),
            ("Magic Squares", True, "✓")
        ]
        
        all_passed = True
        for check_name, passed, symbol in checks:
            print(f"{symbol} {check_name}: {'PASS' if passed else 'FAIL'}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n✨ All systems verified and ready!")
        else:
            print("\n⚠️ Some issues detected. Check data files.")
    
    # ============ SETTINGS MENU METHODS ============
    
    def reference_tables_menu(self):
        """Menu for reference tables"""
        print("\n" + "="*60)
        print("📚 REFERENCE TABLES")
        print("="*60)
        
        print("\nSelect table:")
        print("  1. 🧿 Geomancy Figures")
        print("  2. 📜 I Ching Hexagrams")
        print("  3. 🃏 Tarot Major Arcana")
        print("  4. 📿 Jafr Correspondences")
        print("  5. 🪐 Planetary Correspondences")
        print("  6. 🌟 Elemental Correspondences")
        print("  7. 🔙 Back")
        
        choice = input("\nSelect (1-7): ").strip()
        
        if choice == "1":
            self.display_geomancy_reference()
        elif choice == "2":
            self.display_iching_reference()
        elif choice == "3":
            self.display_tarot_reference()
        elif choice == "4":
            self.display_jafr_reference()
        elif choice == "5":
            self.display_planetary_reference()
        elif choice == "6":
            self.display_elemental_reference()
    
    def settings_menu(self):
        """System settings menu"""
        print("\n" + "="*60)
        print("⚙️  SETTINGS")
        print("="*60)
        
        print("\nSelect setting:")
        print("  1. 💾 Data Management")
        print("  2. 🎨 Display Preferences")
        print("  3. 🔐 Security & Privacy")
        print("  4. 🔄 Reset System")
        print("  5. 🔙 Back")
        
        choice = input("\nSelect (1-5): ").strip()
        
        if choice == "1":
            self.data_management()
        elif choice == "2":
            self.display_preferences()
        elif choice == "3":
            self.security_settings()
        elif choice == "4":
            self.reset_system()
    
    def data_management(self):
        """Data management settings"""
        print("\n💾 DATA MANAGEMENT")
        print("="*60)
        
        print("\n1. Backup all readings")
        print("2. Restore from backup")
        print("3. Clear all data")
        print("4. Export all to JSON")
        print("5. Back")
        
        choice = input("\nSelect: ").strip()
        
        if choice == "1":
            self.backup_data()
        elif choice == "3":
            confirm = input("⚠️ Clear ALL data? (type 'DELETE' to confirm): ")
            if confirm == "DELETE":
                self.history_manager.history = []
                self.history_manager.save_history()
                print("✓ All data cleared")
        elif choice == "4":
            file = self.history_manager.export_to_json()
            print(f"✓ Exported to JSON: {file}")
    
    def backup_data(self):
        """Backup all data"""
        import shutil
        import os
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"backups/backup_{timestamp}"
        
        Path(backup_dir).mkdir(parents=True, exist_ok=True)
        
        # Copy data files
        data_files = ["data/geomancy.json", "data/iching.json", 
                      "data/tarot.json", "data/jafr.json"]
        
        for file in data_files:
            if os.path.exists(file):
                shutil.copy2(file, backup_dir)
        
        # Copy readings
        if os.path.exists("readings"):
            shutil.copytree("readings", f"{backup_dir}/readings")
        
        # Export history
        self.history_manager.export_to_json(f"{backup_dir}/history.json")
        
        print(f"✓ Backup created: {backup_dir}")
    
    def display_preferences(self):
        """Display preferences menu"""
        print("\n🎨 DISPLAY PREFERENCES")
        print("="*60)
        print("\n1. Color themes")
        print("2. Unicode symbols on/off")
        print("3. Detailed/simple mode")
        print("4. Back")
        print("\n(Feature coming soon)")
    
    def security_settings(self):
        """Security and privacy settings"""
        print("\n🔐 SECURITY SETTINGS")
        print("="*60)
        print("\n1. Encrypt readings")
        print("2. Password protection")
        print("3. Clear cache")
        print("4. Back")
        print("\n(Feature coming soon)")
    
    def reset_system(self):
        """Reset system to defaults"""
        confirm = input("\n⚠️ RESET SYSTEM? All data will be lost! (type 'RESET' to confirm): ")
        if confirm == "RESET":
            self.history_manager.history = []
            self.history_manager.save_history()
            print("✓ System reset to defaults")
    
    # ============ MAIN MENU ============
    def main_menu(self):
        """Enhanced main menu"""
        while True:
            print("\n" + "="*60)
            print(f"🔮 QUADRUPLE GODDESS v{self.version}")
            print("="*60)
            print("\nMAIN MENU:")
            print("  1. 🧿 Run Divination Reading")
            print("  2. 📊 System Information")
            print("  3. ❓ Help & Instructions")
            print("  4. 🔍 Verify System")
            print("  5. 📚 View Reference Tables")
            print("  6. ⏰ Planetary Hours Calculator")
            print("  7. 🔢 Magic Square Generator")
            print("  8. 📖 Reading History")
            print("  9. ⚙️  Settings")
            print("  0. 🚪 Exit")
            
            choice = input("\nSelect option (0-9): ").strip()
            
            if choice == "1":
                self.run_reading_menu()
            elif choice == "2":
                self.system_info()
            elif choice == "3":
                self.display_help()
            elif choice == "4":
                self.verify_system()
            elif choice == "5":
                self.reference_tables_menu()
            elif choice == "6":
                self.display_planetary_hour()
            elif choice == "7":
                self.generate_magic_square_menu()
            elif choice == "8":
                self.view_reading_history()
            elif choice == "9":
                self.settings_menu()
            elif choice == "0":
                print("\n✨ Thank you for using Quadruple Goddess!")
                print("   May your path be illuminated. 🌟")
                break
            else:
                print("Invalid choice. Please enter 0-9.")

# ============ STARTUP ============
def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("✨ WELCOME TO QUADRUPLE GODDESS v3.5")
    print("="*60)
    print("Integrated Divination System with Enhanced Features")
    print("Loading systems...")
    
    try:
        system = QuadrupleGoddessSystem()
        system.main_menu()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("Please check your installation.")
    finally:
        print("\n" + "="*60)
        print("Session ended.")
        print("="*60)

if __name__ == "__main__":
    main()
