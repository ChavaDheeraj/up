"""
ontology.py
Theoretical ontology, construct taxonomy, keyword lexicons, and conceptual definitions
for Solo Women Travel Safety Research based on Perceived Risk Theory & Braun & Clarke (2006).
"""

from typing import Dict, Any, List

# Core Higher-Order Constructs and Dimensions
CONSTRUCT_TAXONOMY = {
    "Physical Constraints": {
        "description": "Tangible, environmental, and interpersonal threats to bodily safety, physical integrity, and personal security.",
        "sub_dimensions": {
            "Sexual Harassment & Unwanted Attention": {
                "description": "Catcalling, leering, persistent staring, stalking, groping, sexual comments, and invasive male pursuit.",
                "keywords": [
                    "harassment", "catcall", "catcalling", "stare", "staring", "leer", "leering", 
                    "groped", "grope", "followed", "following me", "stalker", "stalking", 
                    "sexualized", "male attention", "unwanted attention", "creep", "creepy", 
                    "inappropriate touch", "harassed", "men shouting", "men whistling"
                ]
            },
            "Infrastructure & Transit Vulnerability": {
                "description": "Risks associated with public transport, taxis, dark alleys, isolated bus stops, poor lighting, and locked spaces.",
                "keywords": [
                    "dark street", "dimly lit", "unlit", "alley", "isolated", "deserted", 
                    "night train", "taxi scam", "unlicensed taxi", "uber safety", "bus stop", 
                    "public transport", "metro", "subway alone", "walking alone at night", 
                    "no cctv", "secluded", "night walk", "tuk tuk", "rickshaw"
                ]
            },
            "Accommodation & Property Security": {
                "description": "Vulnerabilities in hostels, hotels, vacation rentals, door locks, ground floor rooms, and drink safety.",
                "keywords": [
                    "hotel door", "door lock", "room lock", "hostel dorm", "mixed dorm", 
                    "female dorm", "ground floor", "balcony", "spiked", "drink spiking", 
                    "theft", "stolen", "safe box", "room security", "peep hole", "door wedge"
                ]
            }
        }
    },
    "Social Constraints": {
        "description": "Socio-cultural, patriarchal, normative, and familial restrictions placed on women's autonomous mobility.",
        "sub_dimensions": {
            "Patriarchal Gaze & Cultural Norms": {
                "description": "Conservative societal norms, dress policing, male dominance in public space, and gender discrimination.",
                "keywords": [
                    "patriarchy", "patriarchal", "cultural norms", "conservative culture", 
                    "dress code", "modest dress", "covering up", "shoulders covered", 
                    "male dominated", "public space", "gender role", "gender inequality", 
                    "chauvinism", "taboo", "cultural expectation", "stigma"
                ]
            },
            "Familial Anxiety & Societal Judgment": {
                "description": "Family disapproval, paternalistic protection, fear of victim blaming, and warnings from social circles.",
                "keywords": [
                    "parents worried", "mom freaked out", "family warned", "people said are you crazy", 
                    "dangerous for a girl", "victim blaming", "judged", "reckless", "irresponsible", 
                    "society told me", "relatives concerned", "unaccompanied woman", "why alone"
                ]
            },
            "Racialized & Foreign Vulnerability": {
                "description": "Vulnerabilities stemming from race, ethnicity, language barriers, and stereotyping of foreign women.",
                "keywords": [
                    "foreign woman", "exoticized", "stereotyped", "language barrier", "racism", 
                    "racial", "skin color", "blonde hair", "tourist target", "easy target", "stand out"
                ]
            }
        }
    },
    "Constraint Negotiation & Coping Strategies": {
        "description": "Proactive and reactive behavioral adaptations, micro-strategies, and tools women employ to navigate risk.",
        "sub_dimensions": {
            "Behavioral & Presentation Adaptation": {
                "description": "Altering physical appearance, simulated social ties, purposeful walking, and eye-contact management.",
                "keywords": [
                    "fake wedding ring", "wedding band", "wear headphones", "no music", 
                    "walk with confidence", "walk with purpose", "pretend to know", 
                    "avoid eye contact", "sunglasses", "resting bitch face", "look tough", 
                    "dress like a local", "cover up", "assertive", "set boundaries"
                ]
            },
            "Digital & Communication Tactics": {
                "description": "Leveraging digital tools, location tracking, fake calls, emergency numbers, and backup documentation.",
                "keywords": [
                    "share location", "google maps", "offline maps", "fake phone call", 
                    "pretend to talk", "emergency contact", "sim card", "whatsapp live location", 
                    "safety app", "local sim", "backup phone", "power bank", "itinerary shared"
                ]
            },
            "Spatial & Temporal Planning": {
                "description": "Daylight movement planning, curfew discipline, neighborhood vetting, and transport scheduling.",
                "keywords": [
                    "arrive before dark", "daylight", "never walk at night", "reputable taxi", 
                    "pre booked transfer", "safe neighborhood", "research area", "central location", 
                    "well lit route", "avoid late night", "hostel reviews", "read women reviews"
                ]
            },
            "Intuition & Situational Awareness": {
                "description": "Trusting gut feelings, peripheral alertness, reading atmospheric cues, and knowing when to exit situations.",
                "keywords": [
                    "gut feeling", "trust intuition", "instinct", "situational awareness", 
                    "red flag", "felt uncomfortable", "something felt off", "stay alert", 
                    "trust your gut", "internal alarm", "sixth sense", "listen to intuition"
                ]
            }
        }
    },
    "Perceived Safety": {
        "description": "Subjective cognitive and emotional state of feeling secure, guarded, vulnerable, or at ease in travel spaces.",
        "sub_dimensions": {
            "Subjective Security vs. Vulnerability": {
                "description": "Dynamic sense of personal safety, fluctuating between calm assurance and heightened vigilance.",
                "keywords": [
                    "felt safe", "feel safe", "feeling safe", "safe and sound", "sense of security", 
                    "felt secure", "felt vulnerable", "vulnerability", "feeling unsafe", "scared", 
                    "fear", "terrified", "anxious", "paranoid", "peace of mind", "uncomfortable"
                ]
            },
            "Objective vs. Perceived Risk Calibration": {
                "description": "Deconstructing sensationalized media reports versus the lived reality of everyday safety on the ground.",
                "keywords": [
                    "media says", "news makes it look", "sensationalized", "statistic", 
                    "actual risk", "in reality", "not as scary", "fear mongering", 
                    "perceived danger", "real danger", "rational fear", "irrational fear"
                ]
            }
        }
    },
    "Destination Image & Evaluation": {
        "description": "Consumer perception of destination safety reputation, institutional trust, and host community hospitableness.",
        "sub_dimensions": {
            "Destination Safety Reputation": {
                "description": "Public and peer perception of a country or city as women-friendly, safe, or hazardous.",
                "keywords": [
                    "safest country", "safe destination", "reputation", "dangerous city", 
                    "country ranking", "solo friendly", "female friendly", "women friendly", 
                    "friendly locals", "welcoming", "hospitable", "safety record"
                ]
            },
            "Institutional & Police Trust": {
                "description": "Confidence in local law enforcement, tourist police, emergency healthcare, and public governance.",
                "keywords": [
                    "police", "tourist police", "call the cops", "authorities", "hospital", 
                    "emergency response", "corrupt police", "law enforcement", "help desk"
                ]
            }
        }
    },
    "Travel Intention & Mobility Decisions": {
        "description": "Conative outcomes: destination choice, itinerary modifications, travel avoidance, and future solo travel intentions.",
        "sub_dimensions": {
            "Destination Choice & Route Avoidance": {
                "description": "Selecting or boycotting destinations, canceling trips, or altering routes due to safety considerations.",
                "keywords": [
                    "chose not to visit", "canceled trip", "avoided", "skipped the city", 
                    "changed itinerary", "rerouted", "booked tour instead", "decided to go", 
                    "travel plans", "bucket list", "never going back"
                ]
            },
            "Solo Continuation & Advocacy": {
                "description": "Commitment to future solo travel and recommending solo journeys to other women.",
                "keywords": [
                    "travel again", "future solo trip", "recommend to women", "encourage others", 
                    "every woman should", "keep traveling", "next adventure", "lifelong solo traveler"
                ]
            }
        }
    },
    "Experiential Well-Being & Self-Leadership": {
        "description": "Psychological and transformative outcomes: self-efficacy, autonomy, empowerment, confidence, and flourishing.",
        "sub_dimensions": {
            "Empowerment & Self-Efficacy": {
                "description": "Enhanced sense of agency, pride, capability, self-reliance, and self-leadership through overcoming fear.",
                "keywords": [
                    "empowered", "empowerment", "confidence", "confident", "self reliance", 
                    "self leadership", "independent", "capable", "proud of myself", 
                    "liberating", "freedom", "overcoming fear", "conquered fear", 
                    "transformative", "strength", "growth", "life changing"
                ]
            },
            "Emotional Flourishing & Joy": {
                "description": "Deep psychological well-being, mindfulness, flow, serenity, and joy experienced during independent travel.",
                "keywords": [
                    "peace", "happiness", "joy", "flourishing", "well-being", "mindfulness", 
                    "enriching", "fulfillment", "alive", "gratitude", "mental clarity"
                ]
            }
        }
    }
}

# Theoretical Pathway & Hypotheses for Phase 3 SEM Survey Integration
CONCEPTUAL_HYPOTHESES = [
    {
        "code": "H1",
        "pathway": "Physical Constraints -> Perceived Safety",
        "direction": "negative",
        "formulation": "Higher perceived physical constraints (harassment, transit vulnerabilities, lodging insecurity) significantly reduce perceived safety among solo women travellers."
    },
    {
        "code": "H2",
        "pathway": "Social Constraints -> Perceived Safety",
        "direction": "negative",
        "formulation": "Higher perceived social constraints (patriarchal norms, family anxiety, gender discrimination) negatively affect perceived safety."
    },
    {
        "code": "H3",
        "pathway": "Constraint Negotiation -> Perceived Safety",
        "direction": "positive (mediating/buffering)",
        "formulation": "Active deployment of constraint negotiation strategies (behavioral adaptation, situational awareness, digital tracking) mitigates constraint impact and elevates perceived safety."
    },
    {
        "code": "H4",
        "pathway": "Perceived Safety -> Destination Image",
        "direction": "positive",
        "formulation": "Higher perceived safety positively enhances the cognitive and affective destination image among solo women travellers."
    },
    {
        "code": "H5",
        "pathway": "Destination Image -> Travel Intention",
        "direction": "positive",
        "formulation": "A favorable and safe destination image strongly predicts solo female travel intention."
    },
    {
        "code": "H6",
        "pathway": "Perceived Safety -> Well-Being & Self-Leadership",
        "direction": "positive",
        "formulation": "Enhanced perceived safety during travel fosters greater psychological well-being, empowerment, and self-leadership."
    }
]
