#!/usr/bin/env python3
"""F*cking Gorgeous - Prompt definitions and runner."""
import sys, os, time, argparse
sys.path.insert(0, os.path.dirname(__file__))
from generate_core import generate, OUTPUT_DIR

PROMPTS = {
1:'Coloring page: The word "FUCK" in large bold brush script lettering, surrounded by an intricate mandala of roses, thorny vines, and leaves. Clean black line art on white background, no shading, no grayscale. Detailed petal patterns within mandala rings.',
2:'Coloring page: The word "SHIT" in large bold brush script lettering, surrounded by an intricate mandala of sunflowers, seeds, and leaves. Clean black line art on white background, no shading, no grayscale.',
3:'Coloring page: The word "DAMN" in large bold brush script lettering, surrounded by an intricate mandala of lavender stems, bees, and small flowers. Clean black line art on white background, no shading.',
4:'Coloring page: The word "BITCH" in large bold brush script lettering, surrounded by an intricate mandala of roses, daggers, and thorny vines. Clean black line art, no shading.',
5:'Coloring page: The word "HELL" in large bold brush script lettering, surrounded by an intricate mandala of lilies, flame shapes, and leaves. Clean black line art, no shading.',
6:'Coloring page: The word "ASS" in large bold brush script lettering, surrounded by an intricate mandala of chrysanthemums and leaves. Clean black line art, no shading.',
7:'Coloring page: The word "BASTARD" in large bold brush script lettering, surrounded by an intricate mandala of orchids, hanging vines, and leaves. Clean black line art, no shading.',
8:'Coloring page: The word "CRAP" in large bold brush script lettering, surrounded by an intricate mandala of daisies, butterflies, and leaves. Clean black line art, no shading.',
9:'Coloring page: The word "DOUCHE" in large bold brush script lettering, surrounded by an intricate mandala of lotus flowers, water ripples, and lily pads. Clean black line art, no shading.',
10:'Coloring page: The word "WTF" in large bold brush script lettering, surrounded by an intricate mandala of cherry blossoms, branches, and petals. Clean black line art, no shading.',
11:'Coloring page: The word "OMFG" in large bold brush script lettering, surrounded by an intricate mandala of morning glory vines, flowers, and leaves. Clean black line art, no shading.',
12:'Coloring page: The phrase "HELL NO" in large bold brush script lettering, surrounded by an intricate mandala of tropical hibiscus, plumeria, and palm leaves. Clean black line art, no shading.',
13:'Coloring page: The word "GODDAMN" in large bold brush script lettering, surrounded by an intricate mandala of iris flowers, feathers, and flowing ribbons. Clean black line art, no shading.',
14:'Coloring page: The word "BULLSHIT" in large bold brush script lettering, surrounded by an intricate mandala of peonies, dragonflies, and leaves. Clean black line art, no shading.',
15:'Coloring page: The phrase "PISS OFF" in large bold brush script lettering, surrounded by an intricate mandala of wildflowers, daisies, and grass. Clean black line art, no shading.',
16:'Coloring page: The phrase "Fuck off, I am coloring" in a mix of bold script and clean sans-serif lettering, surrounded by a eucalyptus botanical wreath. Clean black line art, no shading.',
17:'Coloring page: The phrase "Not today, Satan" in a mix of bold script and sans-serif, surrounded by a gothic rose wreath with thorns. Clean black line art, no shading.',
18:'Coloring page: The phrase "Sorry, I cannot. I have plans" in modern script, surrounded by a lavender botanical wreath. Clean black line art, no shading.',
19:'Coloring page: The phrase "Zero fsgiven" in bold script, surrounded by dandelion seeds and dandelion wreath. Clean black line art, no shading.',
20:'Coloring page: The phrase "I am not arguing, I am explaining" in modern script and sans-serif, surrounded by ferns and ivy border. Clean black line art, no shading.',
21:'Coloring page: The phrase "Resting b face" in bold script, surrounded by a poppy wreath. Clean black line art, no shading.',
22:'Coloring page: The phrase "Please leave" in elegant script, surrounded by monstera leaves border. Clean black line art, no shading.',
23:'Coloring page: The phrase "I need a drink" in bold script, surrounded by hibiscus and cocktail glass elements. Clean black line art, no shading.',
24:'Coloring page: The phrase "Nope. Not happening." in bold block lettering, surrounded by cactus and succulent wreath. Clean black line art, no shading.',
25:'Coloring page: The phrase "Boss b energy" in bold script, surrounded by roses and crown shapes wreath. Clean black line art, no shading.',
26:'Coloring page: The phrase "Too glam to give a damn" in elegant script, surrounded by peonies and pearl elements. Clean black line art, no shading.',
27:'Coloring page: The phrase "I do what I want" in bold script, surrounded by tropical leaf border. Clean black line art, no shading.',
28:'Coloring page: The phrase "You had one job" in sans-serif and script, surrounded by olive branches wreath. Clean black line art, no shading.',
29:'Coloring page: The phrase "Adulting is hard" in casual script, surrounded by coffee cup and flowers border. Clean black line art, no shading.',
30:'Coloring page: The phrase "That is the tea" in modern script, surrounded by tea roses and teacup wreath. Clean black line art, no shading.',
31:'Coloring page: The quote "Self-care is telling people to go away" in modern sans-serif, framed by a rose archway with vines. Clean black line art, no shading.',
32:'Coloring page: The quote "Color your stress away" in flowing script, surrounded by wildflower garland. Clean black line art, no shading.',
33:'Coloring page: The quote "Inhale calm, exhale nonsense" in elegant script, enclosed in a lotus mandala border. Clean black line art.',
34:'Coloring page: The quote "Namaste away from me" in modern script, surrounded by zen garden with cacti and stones. Clean black line art.',
35:'Coloring page: The quote "I meditate so I do not punch people" in casual script, surrounded by cherry blossom circle. Clean black line art.',
36:'Coloring page: The quote "Healing looks a lot like saying no" in elegant script, surrounded by dried flower wreath. Clean black line art.',
37:'Coloring page: The quote "Boundaries are sexy" in bold script, framed by thorned rose border. Clean black line art.',
38:'Coloring page: The quote "Protect your peace" in flowing script with smaller text below, enclosed in peace lily mandala. Clean black line art.',
39:'Coloring page: The quote "Glow up or go away" in bold script, surrounded by sunflower burst. Clean black line art.',
40:'Coloring page: The quote "Self-love means no nonsense" in elegant script, enclosed in dahlia circle. Clean black line art.',
41:'Coloring page: The quote "You are a badass, now color" in bold mixed lettering, surrounded by tiger lilies and stars frame. Clean black line art.',
42:'Coloring page: The quote "Keep going" in bold script, surrounded by morning glory spiral. Clean black line art.',
43:'Coloring page: The quote "Strong as can be" in bold block lettering, surrounded by protea and shield leaf patterns. Clean black line art.',
44:'Coloring page: The quote "She believed she could, so she did" in elegant flowing script, surrounded by bougainvillea. Clean black line art.',
45:'Coloring page: The quote "Dream big, work hard, give zero" in bold script, surrounded by sunflowers and stars. Clean black line art.',
46:'Coloring page: The word "UNSTOPPABLE" in bold geometric lettering, surrounded by intricate orchid mandala. Clean black line art.',
47:'Coloring page: The quote "Make it happen" in bold script, surrounded by peony pattern. Clean black line art.',
48:'Coloring page: The quote "Warrior, not worrier" in bold script, surrounded by lavender and swords. Clean black line art.',
49:'Coloring page: The quote "You got this, you gorgeous thing" in bold script, surrounded by rose crown wreath. Clean black line art.',
50:'Coloring page: The quote "Sparkle" in bold script, surrounded by diamond and flower shapes. Clean black line art.',
51:'Coloring page: Full-page artistic quote "Color your stress away" in large decorative script, surrounded by mixed wildflowers, roses, sunflowers radiating outward. Clean black line art.',
52:'Coloring page: Full-page quote "Life is short. Color more. Swear more." in clean sans-serif, surrounded by minimalist botanical line art. Clean black line art.',
53:'Coloring page: Full-page quote "Behind every successful woman is determination" in elegant script, enclosed in wreath mandala with roses and ribbons. Clean black line art.',
54:'Coloring page: Full-page quote "Art is how we decorate our freedom" in art nouveau style, framed by ornate floral border. Clean black line art.',
55:'Coloring page: Full-page quote "Perfect is boring. Color outside the lines." in bold rebellious lettering with wild organic floral chaos. Clean black line art.',
}

COVER_PROMPT = 'Professional coloring book cover design: The words "F-ING GORGEOUS" in large bold ornate script lettering, each letter formed from intertwined roses, lilies, and foliage. Surrounding floral mandala border extending to edges. Subtitle "A Swear Word and Floral Coloring Book for Stressed-Out Adults" below. Clean black line art on white background. Coloring book cover style. Portrait orientation.'

def main():
    p = argparse.ArgumentParser(description="Generate coloring book images")
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--end", type=int, default=55)
    p.add_argument("--cover", action="store_true")
    p.add_argument("--delay", type=float, default=3.0)
    p.add_argument("--retry", type=int, default=2)
    a = p.parse_args()
    
    bk = "Higgsfield" if os.environ.get("HIGGSFIELD_API_KEY") else "DALL-E 3" if os.environ.get("OPENAI_API_KEY") else "NONE"
    print(f"=== Generator ({bk}) ===")
    print(f"Output: {OUTPUT_DIR.absolute()}")
    
    if a.cover:
        print("Generating cover...")
        generate(COVER_PROMPT, "cover-front")
        print("Done!")
        return
    
    ok = 0; bad = []
    for i in range(a.start, a.end + 1):
        if i not in PROMPTS:
            print(f"  Skip {i}: no prompt")
            continue
        print(f"[{i}/{a.end}] Design {i}")
        for att in range(1, a.retry + 1):
            try:
                generate(PROMPTS[i], f"design_{i:02d}")
                ok += 1
                break
            except Exception as e:
                print(f"  Attempt {att}/{a.retry} failed: {e}")
                if att < a.retry:
                    print(f"  Retrying in 10s...")
                    time.sleep(10)
                else:
                    bad.append(i)
                    print(f"  FAILED design {i}")
        time.sleep(a.delay)
    
    print(f"\nDone! {ok} success, {len(bad)} failed")
    if bad: print(f"Failed: {bad}")

if __name__ == "__main__":
    main()
