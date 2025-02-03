def wave_animation(text):
    frames = []
    for i in range(len(text)):
        frame = text[:i].lower() + text[i].upper() + text[i+1:].lower()
        frames.append(frame)
    return frames

def blink_animation(text):
    return [text, " " * len(text)] * 3 + [text]

animations = [
    {'name': 'Волна', 'function': wave_animation},
    {'name': 'Мигание', 'function': blink_animation}
]
