"""
Animation Presets for Nexus Wheel.
"""

ANIMATION_PRESETS = {
    "GTA V Classic": {
        "open_duration": 220,
        "close_duration": 160,
        "segment_transition_speed": 160,
        "hover_animation_speed": 120,
        "scale_animation": True,
        "rotation_animation": True,
        "start_scale": 0.82,
        "start_rotation": -15.0,
        "glow_intensity": 0.85,
        "blur_transition": True,
        "selection_animation": True,
        "easing_type": "OutCubic"
    },
    "Smooth Glass": {
        "open_duration": 300,
        "close_duration": 220,
        "segment_transition_speed": 220,
        "hover_animation_speed": 180,
        "scale_animation": True,
        "rotation_animation": False,
        "start_scale": 0.90,
        "start_rotation": 0.0,
        "glow_intensity": 0.70,
        "blur_transition": True,
        "selection_animation": True,
        "easing_type": "OutQuad"
    },
    "Cyberpunk": {
        "open_duration": 160,
        "close_duration": 120,
        "segment_transition_speed": 100,
        "hover_animation_speed": 80,
        "scale_animation": True,
        "rotation_animation": True,
        "start_scale": 0.75,
        "start_rotation": 25.0,
        "glow_intensity": 1.0,
        "blur_transition": True,
        "selection_animation": True,
        "easing_type": "OutBack"
    },
    "Minimal": {
        "open_duration": 130,
        "close_duration": 100,
        "segment_transition_speed": 120,
        "hover_animation_speed": 90,
        "scale_animation": False,
        "rotation_animation": False,
        "start_scale": 1.0,
        "start_rotation": 0.0,
        "glow_intensity": 0.40,
        "blur_transition": False,
        "selection_animation": True,
        "easing_type": "Linear"
    },
    "Ultra Fast": {
        "open_duration": 70,
        "close_duration": 50,
        "segment_transition_speed": 50,
        "hover_animation_speed": 40,
        "scale_animation": True,
        "rotation_animation": False,
        "start_scale": 0.95,
        "start_rotation": 0.0,
        "glow_intensity": 0.60,
        "blur_transition": False,
        "selection_animation": False,
        "easing_type": "OutQuad"
    }
}
