# Vision

Load for image classification, segmentation, reconstruction, CNN/ViT selection,
or image preprocessing and training-mode contracts. Training/recovery mechanics
remain in [training.md](training.md); image-specific comparison and robustness
claims go to evaluate-deep-learning.

## Choose the task and architecture

A CNN is a useful local/spatial baseline, especially with a modest dataset and
resolution. A ViT represents images as patch tokens and makes patch size,
position encoding, resolution and data/regularization choices part of the
contract. Select it when global interactions or a compatible pretrained path
serve the hypothesis. The original
[ViT paper](https://arxiv.org/abs/2010.11929) motivates the patch-transformer
family; it does not prove that a small scratch-trained ViT beats the baseline.

| Task | Objective | Eligible unit and output |
|---|---|---|
| Single-label classification | Cross-entropy over classes | One valid image; logits `(B, classes)` |
| Multi-label classification | Per-label binary cross-entropy | Explicit observed labels; absent labels need a missingness contract |
| Semantic segmentation | Pixel cross-entropy, optionally a declared overlap term | Valid annotated pixels; output resolution and ignore-index mask |
| Reconstruction | Squared/absolute error or a specified likelihood | Observed target pixels/channels; scaling and corrupt-input construction |

Dice/IoU-style objectives have different denominators from pixel CE. State
class/background/empty-region handling. Reconstruction quality depends on the
pixel likelihood/range; a convenient MSE does not define perceptual fidelity.

## Implementation contract

State channel order, color space, integer-to-float conversion, intensity range,
resize/crop interpolation and label mapping. NNX convolution defaults and a
checkpoint's expected preprocessing must be read for the selected model rather
than inferred from another framework. Record shape `(B,H,W,C)` where used; a
reshape is not a channel-axis transpose. ViT patch dimensions must match the
chosen resolution, with positional embedding adaptation stated if changing it.

Fit learned normalization only on training data. Apply stochastic augmentation
to training inputs, using explicit keys; fixed validation preprocessing gives a
stable evaluation unit. When an augmentation transforms a segmentation image,
apply the aligned geometric transform to the label map using categorical-safe
resampling. Color transforms need not be applied to masks. Domain knowledge
sets permissible rotations/crops: a class or scientific measurement can change
under a visually plausible transform.

Declare BatchNorm statistics updates and dropout train/eval mode. Validation
uses the fitted statistics and deterministic model mode unless the evaluation
protocol intentionally studies stochastic predictions. Multiple crops/views
must aggregate to the stated image/subject unit rather than multiplying the
validation sample size.

## Correctness and scale paths

Inspect a tiny preprocessed batch and its labels; check shapes, ranges, finite
loss/gradients and fixed-fixture learning. For segmentation, assert exact
alignment on an image with a hand-positioned labeled region and verify ignored
pixels do not change the objective. Separate images by subject/source when
those groups define deployment. Near duplicates and patches from one image
belong to the same split contract.

[Flax's NNX ViT example](https://flax.readthedocs.io/en/stable/examples/vit_training.html)
is a primary implementation pointer. [Big Vision](https://github.com/google-research/big_vision)
is a JAX/Flax research codebase with GPU/TPU-scale configurations and project
checkpoint documentation; use its stated working commit/configuration for the
selected model. These pointers are not locally executed examples in this
skill's six-block CPU gate. A pretrained transfer requires an actual architecture,
weight layout, preprocessing and logit/feature parity check. The presence of a
model on an artifact hub alone does not establish a JAX loader.

Typical failures are train/validation preprocessing mismatch, augmentations that
change labels, interpolated class IDs, a silent resolution change, normalization
statistics learned from validation, and aggregate pixel scores that hide a
failed minority class or subject group.
