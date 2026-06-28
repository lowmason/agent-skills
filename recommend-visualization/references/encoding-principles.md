# Encoding principles — why one chart beats another

Chart selection is applied perception. These principles decide ties in
[chart-selection.md](chart-selection.md) and shape the encoding map every recommendation carries.

## The perceptual-channel hierarchy

People decode some visual channels more accurately than others. The classic ranking, from graphical-
perception experiments (Cleveland & McGill 1984; synthesized in Munzner 2014, *Visualization
Analysis and Design*, ch. 5; Wilke 2019, *Fundamentals of Data Visualization*, ch. 2):

**position > length > angle / slope > area > color hue / saturation > volume**

Practical consequences:

- Put the variable the reader must judge most precisely on the **highest-ranked free channel** —
  usually position (a scatter axis) or length on a common baseline (a bar).
- This is the whole case for **bar over pie** (length/position vs. angle/area) and for **2D position
  over a 3rd dimension** (never encode a quantity as depth).
- **Color is a weak quantitative channel** — fine for a *category* (nominal) or a coarse magnitude
  (a heatmap), poor for values you need to compare precisely. Don't ask color to carry the headline
  number.
- **Area encodes magnitude ~½ as accurately as length** — treemaps and bubble charts are
  space-efficient but read imprecisely; reach for them only when the structure (nesting, two
  positional dims already spent) leaves no better channel.

## Color, used deliberately

Match the scale type to the data (Wilke 2019, chs. 4 & 19):

- **Categorical / nominal** → a qualitative palette with distinct hues, **colorblind-safe** (e.g.
  Okabe–Ito, or Tableau-10). Cap it at ~7 hues; beyond that, hues blur — facet or group instead.
- **Sequential** (a magnitude) → a single-hue or perceptually-uniform ramp (**viridis**, cividis).
  Avoid rainbow/jet: it isn't perceptually uniform and invents banding that isn't in the data.
- **Diverging** (a deviation around a meaningful midpoint — change, surplus/deficit) → a two-hue
  diverging ramp centered on zero. Don't use a diverging ramp for data without a natural middle.
- **~8% of men are red-green colorblind.** Never encode meaning by red-vs-green alone; pair hue with
  another channel (position, shape, direct labels) and check a CVD simulation.

## Direct labeling over legends

A legend forces a round-trip: eye to mark, eye to legend, match color, back. **Label the marks
directly** wherever the layout allows — the end of each line, atop each bar — so the name sits where
the data is (Wilke 2019, ch. 20, "Redundant coding"). Legends are the fallback when marks overlap too
much to label. This is a concrete reason small multiples beat a colored multi-line past a few series:
each panel is self-labelled and needs no legend at all (Wilke 2019, ch. 21, "Multi-panel figures").

## Maximize the data-ink ratio (within reason)

Most of the ink should encode data (Tufte 1983, *The Visual Display of Quantitative Information*).
Remove what doesn't inform: heavy gridlines, chart borders, redundant tick labels, drop shadows,
3D bevels, background fills. But don't strip so far that you lose a baseline, a needed gridline, or a
direct label — the goal is clarity, not minimalism for its own sake.

## Sorting, baselines, and aspect ratio

- **Sort by value, not alphabetically**, unless the category has an inherent order (months, sizes).
  A sorted bar chart *is* the ranking; an alphabetical one hides it.
- **Bars start at zero** — they encode by length, so a truncated baseline misstates ratios. A line
  chart encodes by position and may zoom its y-range when the variation is small relative to the
  level.
- **Aspect ratio matters for trends.** "Banking to ~45°" makes slope comparisons easiest (Cleveland);
  a too-tall or too-wide time series misleads about rate of change.

## A standing checklist

1. Is the headline quantity on the **highest-ranked channel** available?
2. Could a **direct label** replace the legend?
3. Is the **color scale** the right type, colorblind-safe, and (if sequential) zero-anchored?
4. Are bars **zero-based** and categories **sorted by value**?
5. Is there **ink that encodes nothing** to remove?
6. Does any caveat from the profile (skew → log, nulls → footnote, large n → density) show **on the
   chart**, not just in your head?

> Vega-Lite — Altair's grammar — formalizes exactly this mark + encoding-channel model (Satyanarayan
> et al. 2017, "Vega-Lite: A Grammar of Interactive Graphics", *IEEE TVCG* 23(1):341–350), which is
> why the encoding map from [chart-selection.md](chart-selection.md) translates almost directly into
> an Altair spec.
