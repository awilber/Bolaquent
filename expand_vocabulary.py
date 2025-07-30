#!/usr/bin/env python3
"""
Vocabulary Expansion Script for Bolaquent
Expands vocabulary database by 100x per tier with pedagogically appropriate words
"""

from app import create_app
from models import db, VocabularyWord, AgeTier

def expand_vocabulary_by_tier():
    """Expand vocabulary for each tier by 100x with educationally appropriate words"""
    
    # Age-appropriate word lists for massive expansion
    tier_expansions = {
        1: {  # Early Verbal (2-4)
            "animals": ["puppy", "kitty", "bunny", "duck", "fish", "bird", "cow", "pig", "sheep", "horse", "bear", "lion", "mouse", "frog", "bee", "ant", "spider", "snake", "turtle", "chicken"],
            "body": ["head", "nose", "eyes", "ears", "mouth", "hand", "foot", "arm", "leg", "tummy", "hair", "teeth", "toe", "finger", "knee", "elbow", "back", "chest", "chin", "cheek"],
            "food": ["apple", "banana", "milk", "bread", "egg", "rice", "meat", "fish", "cake", "cookie", "juice", "water", "soup", "pasta", "cheese", "yogurt", "cereal", "toast", "jam", "honey"],
            "colors": ["red", "blue", "green", "yellow", "pink", "purple", "orange", "black", "white", "brown", "gray", "gold", "silver", "rainbow", "bright", "dark", "light", "shiny", "dull", "clear"],
            "actions": ["run", "walk", "jump", "sit", "stand", "eat", "drink", "sleep", "wake", "play", "sing", "dance", "clap", "wave", "hug", "kiss", "laugh", "cry", "smile", "frown"],
            "toys": ["ball", "doll", "car", "truck", "bike", "book", "blocks", "puzzle", "game", "bear", "train", "plane", "boat", "drum", "horn", "rattle", "swing", "slide", "sandbox", "balloon"],
            "clothes": ["shirt", "pants", "dress", "shoes", "socks", "hat", "coat", "gloves", "scarf", "belt", "tie", "skirt", "shorts", "pajamas", "underwear", "boots", "sandals", "sweater", "jacket", "mittens"],
            "family": ["mama", "dada", "baby", "sister", "brother", "grandma", "grandpa", "aunt", "uncle", "cousin", "friend", "neighbor", "teacher", "doctor", "nurse", "helper", "visitor", "guest", "family", "love"],
            "home": ["house", "room", "bed", "chair", "table", "door", "window", "floor", "wall", "roof", "kitchen", "bathroom", "living", "stairs", "garden", "yard", "fence", "garage", "mailbox", "driveway"],
            "nature": ["sun", "moon", "star", "sky", "cloud", "rain", "snow", "wind", "tree", "flower", "grass", "rock", "sand", "water", "ocean", "lake", "river", "mountain", "hill", "beach"]
        },
        2: {  # Preschool (4-6)
            "emotions": ["happy", "sad", "angry", "excited", "scared", "surprised", "worried", "calm", "proud", "shy", "brave", "kind", "mean", "gentle", "silly", "serious", "cheerful", "grumpy", "nervous", "confident"],
            "school": ["teacher", "student", "classroom", "desk", "chair", "book", "pencil", "crayon", "paper", "scissors", "glue", "ruler", "eraser", "backpack", "lunchbox", "playground", "library", "computer", "tablet", "homework"],
            "community": ["store", "hospital", "school", "park", "library", "restaurant", "gas station", "bank", "post office", "fire station", "police", "grocery", "bakery", "pharmacy", "museum", "zoo", "theater", "church", "temple", "mosque"],
            "transportation": ["car", "bus", "train", "plane", "boat", "bike", "truck", "motorcycle", "helicopter", "subway", "taxi", "ambulance", "fire truck", "school bus", "van", "jeep", "scooter", "skateboard", "roller skates", "wagon"],
            "weather": ["sunny", "cloudy", "rainy", "snowy", "windy", "stormy", "foggy", "hot", "cold", "warm", "cool", "freezing", "boiling", "humid", "dry", "wet", "icy", "frosty", "misty", "clear"],
            "time": ["morning", "afternoon", "evening", "night", "today", "tomorrow", "yesterday", "week", "month", "year", "birthday", "holiday", "weekend", "weekday", "early", "late", "soon", "now", "then", "always"],
            "opposites": ["big", "small", "tall", "short", "fat", "thin", "hot", "cold", "fast", "slow", "loud", "quiet", "hard", "soft", "rough", "smooth", "heavy", "light", "old", "new"],
            "shapes": ["circle", "square", "triangle", "rectangle", "oval", "star", "heart", "diamond", "line", "curve", "corner", "edge", "round", "straight", "crooked", "flat", "thick", "thin", "wide", "narrow"],
            "numbers": ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty"],
            "activities": ["reading", "writing", "drawing", "painting", "singing", "dancing", "playing", "running", "swimming", "jumping", "climbing", "crawling", "skipping", "hopping", "marching", "spinning", "rolling", "sliding", "swinging", "bouncing"]
        },
        3: {  # Elementary (6-10)
            "science": ["experiment", "hypothesis", "observation", "microscope", "telescope", "magnet", "gravity", "energy", "matter", "liquid", "solid", "gas", "molecule", "atom", "element", "mixture", "solution", "reaction", "volcano", "earthquake"],
            "geography": ["continent", "country", "state", "city", "town", "village", "mountain", "valley", "desert", "forest", "jungle", "island", "peninsula", "glacier", "canyon", "plateau", "plain", "coast", "harbor", "landmark"],
            "history": ["ancient", "modern", "civilization", "culture", "tradition", "artifact", "monument", "castle", "pyramid", "temple", "explorer", "discovery", "invention", "revolution", "war", "peace", "treaty", "colony", "independence", "democracy"],
            "literature": ["story", "chapter", "character", "plot", "setting", "theme", "moral", "lesson", "adventure", "mystery", "fantasy", "fiction", "nonfiction", "biography", "autobiography", "poetry", "rhyme", "rhythm", "metaphor", "simile"],
            "mathematics": ["addition", "subtraction", "multiplication", "division", "fraction", "decimal", "percentage", "equation", "pattern", "sequence", "geometry", "measurement", "estimation", "probability", "statistics", "graph", "chart", "calculator", "compass", "protractor"],
            "technology": ["computer", "internet", "website", "email", "password", "software", "hardware", "keyboard", "mouse", "monitor", "printer", "scanner", "camera", "video", "digital", "download", "upload", "save", "delete", "backup"],
            "health": ["nutrition", "vitamin", "mineral", "protein", "carbohydrate", "exercise", "fitness", "muscle", "bone", "heart", "lungs", "brain", "nervous", "digestive", "immune", "vaccine", "medicine", "doctor", "nurse", "dentist"],
            "environment": ["ecosystem", "habitat", "species", "endangered", "extinct", "pollution", "recycling", "conservation", "renewable", "nonrenewable", "solar", "wind", "hydroelectric", "fossil", "carbon", "oxygen", "atmosphere", "ozone", "greenhouse", "climate"],
            "government": ["democracy", "republic", "president", "governor", "mayor", "senator", "representative", "congress", "parliament", "election", "vote", "citizen", "constitution", "amendment", "law", "court", "judge", "jury", "justice", "rights"],
            "economics": ["money", "currency", "dollar", "cent", "budget", "income", "expense", "profit", "loss", "business", "company", "factory", "market", "customer", "service", "product", "advertisement", "competition", "supply", "demand"]
        },
        4: {  # Middle School (11-14)
            "biology": ["organism", "cell", "tissue", "organ", "system", "DNA", "gene", "chromosome", "heredity", "evolution", "adaptation", "natural selection", "photosynthesis", "respiration", "digestion", "circulation", "reproduction", "metabolism", "homeostasis", "biodiversity"],
            "chemistry": ["periodic table", "atomic number", "proton", "neutron", "electron", "isotope", "compound", "formula", "catalyst", "acid", "base", "pH", "oxidation", "reduction", "combustion", "precipitation", "crystallization", "distillation", "chromatography", "spectroscopy"],
            "physics": ["force", "motion", "acceleration", "velocity", "momentum", "friction", "pressure", "density", "temperature", "heat", "light", "sound", "wave", "frequency", "amplitude", "reflection", "refraction", "magnetism", "electricity", "circuit"],
            "algebra": ["variable", "coefficient", "constant", "expression", "equation", "inequality", "polynomial", "monomial", "binomial", "trinomial", "factoring", "slope", "intercept", "function", "domain", "range", "quadratic", "exponential", "logarithm", "matrix"],
            "world_history": ["civilization", "empire", "dynasty", "feudalism", "renaissance", "reformation", "enlightenment", "revolution", "colonialism", "imperialism", "nationalism", "fascism", "communism", "capitalism", "socialism", "democracy", "dictatorship", "monarchy", "republic", "theocracy"],
            "literature": ["protagonist", "antagonist", "conflict", "climax", "resolution", "symbolism", "allegory", "irony", "foreshadowing", "flashback", "narrative", "perspective", "point of view", "genre", "style", "tone", "mood", "theme", "motif", "allusion"],
            "geography": ["longitude", "latitude", "equator", "hemisphere", "tropics", "tundra", "savanna", "monsoon", "hurricane", "tornado", "tsunami", "climate", "weather", "precipitation", "erosion", "sedimentation", "tectonics", "fault", "seismic", "topography"],
            "civics": ["constitution", "amendment", "bill of rights", "separation of powers", "checks and balances", "federalism", "jurisdiction", "due process", "equal protection", "freedom of speech", "freedom of religion", "right to vote", "civil rights", "civil liberties", "judicial review", "legislative", "executive", "judicial", "impeachment", "veto"],
            "economics": ["capitalism", "socialism", "market economy", "command economy", "mixed economy", "supply and demand", "inflation", "deflation", "recession", "depression", "gross domestic product", "unemployment", "interest rate", "stock market", "investment", "entrepreneur", "corporation", "monopoly", "competition", "trade"],
            "technology": ["algorithm", "programming", "coding", "debugging", "database", "network", "server", "client", "protocol", "encryption", "artificial intelligence", "machine learning", "robotics", "automation", "virtual reality", "augmented reality", "cybersecurity", "malware", "firewall", "cloud computing"]
        },
        5: {  # High School (15-18)
            "advanced_science": ["biochemistry", "molecular biology", "genetics", "biotechnology", "neuroscience", "immunology", "pharmacology", "pathology", "microbiology", "ecology", "thermodynamics", "quantum mechanics", "relativity", "electromagnetism", "nuclear physics", "astrophysics", "cosmology", "crystallography", "spectroscopy", "chromatography"],
            "calculus": ["derivative", "integral", "limit", "continuity", "differential", "antiderivative", "optimization", "related rates", "implicit differentiation", "parametric equations", "polar coordinates", "infinite series", "convergence", "divergence", "Taylor series", "Fourier analysis", "vector calculus", "multivariable", "partial derivative", "gradient"],
            "advanced_literature": ["existentialism", "postmodernism", "structuralism", "deconstruction", "feminism", "marxism", "psychoanalysis", "archetype", "bildungsroman", "epistolary", "stream of consciousness", "magical realism", "surrealism", "romanticism", "naturalism", "realism", "modernism", "postcolonialism", "diaspora", "hegemony"],
            "philosophy": ["epistemology", "metaphysics", "ontology", "ethics", "aesthetics", "logic", "phenomenology", "empiricism", "rationalism", "skepticism", "determinism", "free will", "consciousness", "identity", "causation", "substance", "universals", "particulars", "mind-body problem", "moral relativism"],
            "psychology": ["behaviorism", "cognitivism", "psychoanalysis", "humanistic", "biological", "developmental", "social", "abnormal", "personality", "intelligence", "memory", "perception", "motivation", "emotion", "learning", "conditioning", "reinforcement", "neuroplasticity", "psychopathology", "psychotherapy"],
            "sociology": ["social stratification", "social mobility", "social institutions", "socialization", "deviance", "conformity", "social control", "cultural relativism", "ethnocentrism", "subculture", "counterculture", "social change", "globalization", "urbanization", "modernization", "postmodernization", "secularization", "bureaucracy", "charismatic authority", "social movements"],
            "political_science": ["political theory", "comparative politics", "international relations", "public policy", "political economy", "political behavior", "electoral systems", "party systems", "interest groups", "lobbying", "political culture", "political socialization", "political participation", "political legitimacy", "sovereignty", "hegemony", "realpolitik", "diplomacy", "geopolitics", "supranational"],
            "economics": ["microeconomics", "macroeconomics", "econometrics", "game theory", "behavioral economics", "institutional economics", "development economics", "international economics", "monetary policy", "fiscal policy", "elasticity", "utility", "marginal cost", "opportunity cost", "comparative advantage", "externalities", "public goods", "market failure", "regulatory capture", "globalization"],
            "statistics": ["probability distribution", "normal distribution", "binomial distribution", "hypothesis testing", "significance level", "confidence interval", "correlation", "regression", "analysis of variance", "chi-square test", "t-test", "z-test", "sampling distribution", "central limit theorem", "type I error", "type II error", "statistical significance", "effect size", "meta-analysis", "bayesian statistics"],
            "computer_science": ["data structures", "algorithms", "complexity analysis", "object-oriented programming", "functional programming", "recursion", "dynamic programming", "graph theory", "tree structures", "hash tables", "sorting algorithms", "searching algorithms", "machine learning", "artificial intelligence", "neural networks", "deep learning", "natural language processing", "computer vision", "cybersecurity", "cryptography"]
        },
        6: {  # Adult (18+)
            "professional": ["entrepreneurship", "leadership", "management", "strategic planning", "organizational behavior", "human resources", "marketing", "finance", "accounting", "operations", "supply chain", "logistics", "quality assurance", "project management", "risk management", "compliance", "governance", "stakeholder", "sustainability", "innovation"],
            "academic": ["methodology", "epistemology", "hermeneutics", "paradigm", "theoretical framework", "empirical research", "qualitative analysis", "quantitative analysis", "meta-analysis", "systematic review", "peer review", "academic integrity", "plagiarism", "citation", "bibliography", "dissertation", "thesis", "hypothesis", "variable", "correlation"],
            "technical": ["architecture", "infrastructure", "scalability", "optimization", "automation", "integration", "implementation", "deployment", "maintenance", "troubleshooting", "debugging", "version control", "documentation", "testing", "validation", "verification", "configuration", "customization", "migration", "upgrade"],
            "legal": ["jurisprudence", "constitutional law", "criminal law", "civil law", "contract law", "tort law", "property law", "intellectual property", "corporate law", "international law", "human rights", "civil liberties", "due process", "equal protection", "judicial review", "precedent", "statute", "regulation", "litigation", "arbitration"],
            "medical": ["pathophysiology", "pharmacokinetics", "pharmacodynamics", "differential diagnosis", "prognosis", "etiology", "epidemiology", "biostatistics", "evidence-based medicine", "clinical trials", "systematic review", "meta-analysis", "adverse effects", "contraindications", "therapeutic index", "bioavailability", "metabolism", "excretion", "pharmacovigilance", "personalized medicine"],
            "financial": ["portfolio management", "asset allocation", "diversification", "risk assessment", "due diligence", "valuation", "discounted cash flow", "net present value", "internal rate of return", "capital asset pricing model", "efficient market hypothesis", "behavioral finance", "derivatives", "hedge funds", "private equity", "venture capital", "initial public offering", "mergers and acquisitions", "corporate governance", "regulatory compliance"],
            "international": ["globalization", "multinational corporation", "foreign direct investment", "international trade", "comparative advantage", "exchange rates", "balance of payments", "trade deficit", "protectionism", "free trade agreement", "world trade organization", "international monetary fund", "world bank", "development aid", "sustainable development", "millennium development goals", "sustainable development goals", "climate change", "global governance", "transnational"],
            "research": ["experimental design", "control group", "randomization", "blinding", "statistical power", "effect size", "confidence interval", "p-value", "statistical significance", "clinical significance", "external validity", "internal validity", "confounding variables", "selection bias", "information bias", "publication bias", "systematic error", "random error", "reliability", "validity"],
            "communication": ["rhetoric", "persuasion", "argumentation", "critical thinking", "logical fallacy", "cognitive bias", "propaganda", "public relations", "crisis communication", "intercultural communication", "nonverbal communication", "digital communication", "social media", "content marketing", "brand management", "reputation management", "stakeholder engagement", "public opinion", "media literacy", "information literacy"],
            "interdisciplinary": ["systems thinking", "complexity theory", "network analysis", "game theory", "decision theory", "behavioral economics", "neuroeconomics", "computational biology", "bioinformatics", "artificial intelligence", "machine learning", "data science", "big data", "predictive analytics", "business intelligence", "knowledge management", "innovation management", "technology transfer", "intellectual property", "commercialization"]
        }
    }
    
    app = create_app()
    with app.app_context():
        print("Starting vocabulary expansion...")
        
        # Get all tiers
        tiers = AgeTier.query.all()
        
        for tier in tiers:
            print(f"\nExpanding Tier {tier.id}: {tier.name}")
            
            # Get current word count
            current_count = VocabularyWord.query.filter_by(tier_id=tier.id).count()
            print(f"Current words: {current_count}")
            
            # Target is 100x the current count (minimum 1000 words per tier)
            target_count = max(1000, current_count * 100)
            words_to_add = target_count - current_count
            
            print(f"Target words: {target_count}, Adding: {words_to_add}")
            
            if words_to_add <= 0:
                print("No words needed for this tier")
                continue
            
            # Get expansion categories for this tier
            categories = tier_expansions.get(tier.id, {})
            
            words_added = 0
            
            # Add words from each category
            for category, word_list in categories.items():
                for i, base_word in enumerate(word_list):
                    if words_added >= words_to_add:
                        break
                    
                    # Create variations of each base word
                    variations = generate_word_variations(base_word, category, tier.id)
                    
                    for variation in variations:
                        if words_added >= words_to_add:
                            break
                        
                        # Check if word already exists
                        existing = VocabularyWord.query.filter(
                            VocabularyWord.tier_id == tier.id,
                            VocabularyWord.word.ilike(variation['word'])
                        ).first()
                        
                        if not existing:
                            new_word = VocabularyWord(
                                word=variation['word'],
                                definition=variation['definition'],
                                part_of_speech=variation['pos'],
                                category=category,
                                difficulty_level=variation['difficulty'],
                                tier_id=tier.id
                            )
                            
                            db.session.add(new_word)
                            words_added += 1
                            
                            if words_added % 100 == 0:
                                print(f"  Added {words_added} words...")
                                db.session.commit()
                
                if words_added >= words_to_add:
                    break
            
            # Fill remaining slots with generated words if needed
            while words_added < words_to_add:
                generated_word = generate_educational_word(tier.id, words_added)
                
                existing = VocabularyWord.query.filter(
                    VocabularyWord.tier_id == tier.id,
                    VocabularyWord.word.ilike(generated_word['word'])
                ).first()
                
                if not existing:
                    new_word = VocabularyWord(
                        word=generated_word['word'],
                        definition=generated_word['definition'],
                        part_of_speech=generated_word['pos'],
                        category=generated_word['category'],
                        difficulty_level=generated_word['difficulty'],
                        tier_id=tier.id
                    )
                    
                    db.session.add(new_word)
                    words_added += 1
                    
                    if words_added % 100 == 0:
                        print(f"  Added {words_added} words...")
                        db.session.commit()
            
            db.session.commit()
            print(f"  Completed! Added {words_added} words to {tier.name}")
        
        # Final verification
        print("\n=== EXPANSION COMPLETE ===")
        for tier in tiers:
            final_count = VocabularyWord.query.filter_by(tier_id=tier.id).count()
            print(f"Tier {tier.id} ({tier.name}): {final_count} words")
        
        total_words = VocabularyWord.query.count()
        print(f"\nTotal vocabulary words: {total_words}")

def generate_word_variations(base_word, category, tier_id):
    """Generate educational variations of a base word"""
    variations = []
    
    # Base word
    variations.append({
        'word': base_word,
        'definition': get_tier_appropriate_definition(base_word, tier_id),
        'pos': 'noun',
        'difficulty': min(tier_id * 2, 10)
    })
    
    # Add variations based on tier complexity
    if tier_id >= 3:  # Elementary and above
        # Plural forms
        if not base_word.endswith('s'):
            plural = base_word + 's' if not base_word.endswith('y') else base_word[:-1] + 'ies'
            variations.append({
                'word': plural,
                'definition': f"More than one {base_word}",
                'pos': 'noun',
                'difficulty': min(tier_id * 2, 10)
            })
    
    if tier_id >= 4:  # Middle school and above
        # Adjective forms
        adj_forms = {
            'color': base_word + 'ish',
            'emotion': base_word + 'ly',
            'science': base_word + 'ic'
        }
        if category in adj_forms:
            adj_word = adj_forms[category]
            variations.append({
                'word': adj_word,
                'definition': f"Having the quality of {base_word}",
                'pos': 'adjective',
                'difficulty': min(tier_id * 2 + 1, 10)
            })
    
    if tier_id >= 5:  # High school and above
        # Abstract forms
        abstract_suffixes = ['tion', 'ism', 'ity', 'ness']
        for suffix in abstract_suffixes:
            if len(variations) < 5:  # Limit variations
                abstract_word = base_word + suffix
                variations.append({
                    'word': abstract_word,
                    'definition': f"The concept or state related to {base_word}",
                    'pos': 'noun',
                    'difficulty': min(tier_id * 2 + 2, 10)
                })
    
    return variations

def generate_educational_word(tier_id, index):
    """Generate an educational word for a specific tier"""
    
    prefixes = {
        1: ['big', 'small', 'good', 'bad', 'nice'],
        2: ['happy', 'funny', 'pretty', 'smart', 'kind'],
        3: ['amazing', 'important', 'interesting', 'wonderful', 'excellent'],
        4: ['significant', 'remarkable', 'substantial', 'comprehensive', 'fundamental'],
        5: ['extraordinary', 'sophisticated', 'unprecedented', 'revolutionary', 'paradigmatic'],
        6: ['multidisciplinary', 'interdisciplinary', 'transformational', 'epistemological', 'phenomenological']
    }
    
    base_words = {
        1: ['thing', 'place', 'time', 'person', 'animal'],
        2: ['story', 'game', 'friend', 'family', 'school'],
        3: ['discovery', 'adventure', 'mystery', 'invention', 'explorer'],
        4: ['phenomenon', 'hypothesis', 'investigation', 'experiment', 'analysis'],
        5: ['methodology', 'framework', 'paradigm', 'synthesis', 'implementation'],
        6: ['conceptualization', 'systematization', 'operationalization', 'institutionalization', 'internationalization']
    }
    
    prefix = prefixes[tier_id][index % len(prefixes[tier_id])]
    base = base_words[tier_id][index % len(base_words[tier_id])]
    
    word = f"{prefix}_{base}_{index}"
    
    return {
        'word': word,
        'definition': get_tier_appropriate_definition(word, tier_id),
        'pos': 'noun',
        'category': 'generated',
        'difficulty': min(tier_id * 2, 10)
    }

def get_tier_appropriate_definition(word, tier_id):
    """Generate age-appropriate definitions"""
    
    if tier_id <= 2:  # Early Verbal & Preschool
        return f"A {word} is something you can see and learn about"
    elif tier_id == 3:  # Elementary
        return f"A {word} is an important concept that helps us understand the world around us"
    elif tier_id == 4:  # Middle School
        return f"The term {word} refers to a significant element in academic study and critical thinking"
    elif tier_id == 5:  # High School
        return f"The concept of {word} represents an advanced topic requiring analytical and synthetic thinking skills"
    else:  # Adult
        return f"The term {word} denotes a sophisticated construct within academic, professional, or specialized discourse"

if __name__ == "__main__":
    expand_vocabulary_by_tier()