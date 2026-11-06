"""
add_speaker_notes.py
====================
Adds complete, professional, slide-by-slide speaker scripts into the
'Click to add notes' (Speaker Notes) section of Project_Presentation_Complete.pptx.
Each note includes:
  - Speaking time recommendation
  - Point-by-point spoken script
  - Visual cues for slides with figures/tables
  - Anticipated review questions & defense tips
"""

from pptx import Presentation

PPT_INPUT  = "Project_Presentation_Complete.pptx"
PPT_OUTPUT = "Project_Presentation_Complete_with_Notes.pptx"
prs = Presentation(PPT_INPUT)

NOTES = [
    # ── Slide 1: Title Slide ──────────────────────────────────────────────
    """[SPEAKING TIME: ~30-40 seconds]

"A very pleasant good morning/afternoon to respected Dr. Arun Nimmala sir and our honorable review panel.

We are Team B4 from the Department of Electronics and Communication Engineering, K L University. Our team members are Velivala Keerthi, Shaik Hanifa, K. Dinesh, and myself, T. Venkata Ram Charan Reddy.

Today, we are presenting our end-to-end research project entitled: 'Sensitivity-Guided Layer-Wise Approximate Multiplier Mapping for FPGA-Based CNN Accelerators.'

In this presentation, we will walk you through our complete hardware-software co-design framework: from 8x8 approximate multiplier RTL characterization and INT8 quantization, to our single-pass 0.2-second sensitivity scoring formula, NSGA-II Pareto optimization, and our synthesizable AXI4-Stream accelerator designed for the PYNQ-Z2 FPGA board."
""",

    # ── Slide 2: Problem Definition & Motivation ──────────────────────────
    """[SPEAKING TIME: ~45-60 seconds]

"To begin with the problem context: Deploying deep convolutional neural networks on resource-constrained edge devices is heavily bottlenecked by power and silicon area. In modern CNNs, convolutional layers account for over 99.8% of all multiply-accumulate—or MAC—operations. Inside each MAC unit, the 8x8 multiplier is by far the most expensive component, consuming 68 Look-Up Tables on our target Xilinx Zynq-7020 FPGA.

Approximate computing presents an attractive solution: by strategically simplifying the multiplier's arithmetic logic, we can achieve substantial silicon area and energy reductions. Because neural networks possess inherent noise resilience, they can tolerate minor numerical inaccuracies without sacrificing classification accuracy.

However, the core open challenge in literature is: Which layer gets which multiplier?
If you apply a single approximate multiplier uniformly across all layers, the network either suffers catastrophic accuracy collapse if the approximation is aggressive, or achieves negligible hardware savings if it is mild.

Existing state-of-the-art solutions have severe limitations:
Evolutionary search methods, such as ALWANN published in ICCAD 2019, take up to 7.5 CPU-days to explore the configuration space. On the other hand, gradient-based retraining methods like TRAM demand full GPU retraining loops and access to proprietary training data.

Our goal is to eliminate this overhead entirely: mapping approximate multipliers intelligently in a single pass without retraining."
""",

    # ── Slide 3: Project Objectives & Technical Scope ──────────────────────
    """[SPEAKING TIME: ~45 seconds]

"Our primary objective is to formulate a lightweight, single-pass sensitivity scoring metric computed in just 0.2 seconds without retraining or iterative search, to assign the optimal approximate multiplier to each convolutional layer.

Our technical scope covers four tightly integrated domains:
1. In VLSI RTL: Designing, exhaustively simulating, and synthesizing a parameterizable 8x8 approximate multiplier library in Verilog.
2. In Deep Learning: Implementing affine INT8 quantization on a 4-convolutional layer Fashion-MNIST network matching our unsigned hardware datapath.
3. In Optimization: Constructing an NSGA-II multi-objective genetic algorithm exploring 256 configurations as a ground-truth baseline.
4. In Hardware Deployment: Implementing an AXI4-Stream accelerator IP core for physical deployment on the PYNQ-Z2 FPGA board.

Our scope is intentionally focused: we approximate only the convolutional layers because Dense layers account for less than 0.13% of MACs. Furthermore, all downstream hardware work was strictly gated behind empirical validation."
""",

    # ── Slide 4: Literature Review & Research Gap ──────────────────────────
    """[SPEAKING TIME: ~60 seconds]
[CUE: Refer to the comparison table on the slide, specifically highlighting the bottom row]

"Looking at the literature, five foundational works define our research gap, as summarized in this table:

1. ALWANN (Mrazek et al., ICCAD 2019) used NSGA-II search over 36 designs, but required 7.5 CPU-days of search time and was never deployed on real FPGA silicon.
2. TRAM (Meng et al., 2026) made multipliers trainable, but requires full GPU retraining loops.
3. Meng et al. (2025) developed LUT-based gradient estimators, but their own paper explicitly states that retraining estimators are complementary to selection algorithms, not a replacement for them.
4. Sayadi et al. in Scientific Reports 2025 used weight variance drop rules, but because static weights ignore task loss, their method caused noticeable accuracy drops and still required gradual retraining.
5. Kumari & Rao in 2025 deployed on a PYNQ FPGA, but applied approximation uniformly across the entire network with zero layer-wise selection intelligence.

As shown in the highlighted last row: Our framework is the only one that achieves all four criteria simultaneously: search-free (0.2s runtime), retraining-free post-training execution, heterogeneous layer-wise assignment, and validation on real PYNQ-Z2 FPGA silicon."
""",

    # ── Slide 5: Proposed Co-Design Methodology ────────────────────────────
    """[SPEAKING TIME: ~50-60 seconds]

"Our proposed co-design methodology operates in four distinct stages:

In Stage 1, we train our 4-conv baseline CNN on Fashion-MNIST (achieving 84.69% exact accuracy) and quantize activations to unsigned INT8 and weights to sign-magnitude format. We extract a tiny calibration batch of 256 images to enable fast probing without touching the 60,000-image training set.

In Stage 2, we compute our sensitivity metric, S3. Our formula couples two vital perspectives:
  S3(l) = 0.5 * norm(Var(W_l)) + 0.5 * norm(||∇_{W_l} L||)
Weight variance captures static parameter distribution, while gradient magnitude measures dynamic loss sensitivity via a single backward pass. This entire probe completes in just 0.2 seconds on a standard CPU.

In Stage 3, we rank the layers from most sensitive to least sensitive:
The most sensitive layer receives an Exact multiplier to safeguard accuracy, intermediate layers receive Compensated designs, and the most resilient layer receives an aggressive Truncated multiplier.

Finally, in Stage 4, this heterogeneous assignment is mapped onto our FPGA processing elements with 2-bit runtime mode control."
""",

    # ── Slide 6: CNN Architecture & Layer Multiplier Mapping (Fig 7) ───────
    """[SPEAKING TIME: ~60 seconds]
[CUE: Direct the panel's attention to Figure 7 across the bottom of the slide]

"Figure 7 illustrates our complete CNN architecture alongside the layer-wise sensitivity scores and hardware multiplier assignments:

Our network consists of 4 convolutional layers with 3x3 kernels and ReLU activations, followed by Global Average Pooling and two Dense layers.

Now, observe the crucial contrast between conv1 and conv4:
conv1 extracts raw spatial edges and textures. It performs 112,000 MACs—which is only 3.0% of the network total. However, our sensitivity probe revealed that conv1 has a sensitivity score of 1.000—it is overwhelmingly the most vulnerable layer because any arithmetic noise here cascades through the entire network. Therefore, we assign conv1 an EXACT multiplier.

In stark contrast, look at conv4:
conv4 performs 1.8 million MACs—which is 48.5% of all multiplications in the entire network! Yet, its sensitivity score is only 0.014. Because conv4 operates on high-level abstract representations and is followed by Global Average Pooling, arithmetic noise is naturally averaged out.

By assigning our aggressive Truncated-6 multiplier to conv4, we cut the multiplier area of nearly half the entire network by 32.5%, while keeping baseline classification accuracy completely intact."
""",

    # ── Slide 7: RTL Multiplier Library & Error Analysis (Fig 1) ───────────
    """[SPEAKING TIME: ~60 seconds]
[CUE: Point to the error distribution plots on the left (Fig 1) and the characterization table on the right]

"Slide 7 presents our hardware characterization results across all four 8x8 multiplier architectures, exhaustively simulated across all 65,536 input combinations.

On the left, Figure 1 shows the error distributions for Truncated, Compensated, and OR-based designs at truncation depth T=6:
Notice that Truncated has a strong negative mean error of -80.25 because low-order partial products are strictly deleted. Compensated shifts the distribution back toward zero, reducing mean error to -48.25. OR-based introduces a massive positive error of +160.50.

Now, look at the synthesis table on the right. This contains our most significant circuit-level finding:
An exact 8x8 multiplier consumes 68 LUTs. Truncated-6 reduces this to 46 LUTs—a 32.5% area saving.
Look at Compensated-6: it consumes the EXACT SAME 46 LUTs as Truncated, yet cuts arithmetic error by 35%!
Why? Because adding the constant compensation bias of +32 requires zero extra logic gates—the synthesis tool folds the constant directly into the carry-in bit of the existing adder tree for free.

Therefore, we proved that Compensated strictly dominates Truncated at no extra hardware cost, while OR-based is dominated on all counts."
""",

    # ── Slide 8: INT8 Quantization & Probing Mechanics ──────────────────────
    """[SPEAKING TIME: ~45 seconds]

"Slide 8 details how we bridge software neural network inference with fixed-point hardware:

First, for activations: Because ReLU outputs are non-negative, activations map naturally to unsigned 8-bit integers from 0 to 255 using affine scaling: x_q = clip(round(x / scale_x), 0, 255).

Second, for weights: Weights are signed (+ and -). Standard signed multipliers require expensive Booth recoding logic. Instead, we use a Sign-Magnitude scheme:
We extract the sign bit separately, and quantize the absolute magnitude |w| into an unsigned 8-bit integer [0, 255]. The unsigned 8x8 hardware multiplier computes activation times weight magnitude, and the 1-bit sign simply controls whether the 32-bit accumulator performs addition or subtraction. This saves approximately 22% silicon area over two's complement multipliers.

Finally, our sensitivity probing uses TensorFlow's GradientTape across 256 calibration images, computing loss gradients with respect to each layer's weights in a single backward pass of 0.2 seconds, with zero retraining epochs."
""",

    # ── Slide 9: Layer Sensitivity Heatmap (Fig 2) ─────────────────────────
    """[SPEAKING TIME: ~50 seconds]
[CUE: Point to the heatmap in Figure 2 and the accompanying numerical table]

"Figure 2 displays the sensitivity distribution across all four convolutional layers for our five candidate metrics, S1 through S5:

Notice the steep drop in sensitivity across the network hierarchy:
conv1 receives a score of 1.000 across metrics S1, S2, S3, and S5. It is unambiguously the most sensitive layer.
conv2 drops significantly to 0.180.
conv3 and conv4 drop to near-zero: 0.008 and 0.014 respectively.

This aligns perfectly with deep learning theory: early layers extract fragile texture and edge primitives where arithmetic errors corrupt subsequent feature representations. Deep layers feature high channel redundancy, allowing approximation noise in some channels to be compensated by others.

Furthermore, our proposed metric, S3, successfully balances static weight variance (S1) and dynamic loss gradient (S2), avoiding the contradictory ranking observed in activation variance (S4)."
""",

    # ── Slide 10: Validation Sweep: The Noise Floor Discovery (Fig 3) ──────
    """[SPEAKING TIME: ~60 seconds]
[CUE: Direct attention to the side-by-side matrices in Figure 3, contrasting (a) and (b)]

"Slide 10 details our most critical experimental diagnosis—what we call 'The Noise Floor Discovery.'

Initially, we evaluated our 12-cell layer-by-layer validation matrix using the mild TRUNC=4 multiplier library, shown in Figure 3(a):
The resulting accuracy drops were extremely small—hovering between -0.34% to +0.17%. In fact, conv3 with OR-based approximation appeared to 'improve' accuracy by 0.34%! This was pure binomial statistical noise. The network was so resilient to TRUNC=4 that the error signal was completely buried below the noise floor, resulting in an initial NO-GO correlation.

Rather than treating this as a failure of our hypothesis, we recognized it as an engineering characterization of the noise boundary. You cannot correlate a ranking score against noise.

To resolve this, we scaled our library to TRUNC=6, dropping 21 partial products and amplifying NMED by 6.6x, shown in Figure 3(b):
With TRUNC=6, a clear, measurable damage signal emerged: conv1 suffered a heavy 1.85% accuracy drop, while conv4 dropped only 0.41%. This confirmed that when approximation error is strong enough to be detected, sensitivity scores accurately predict layer degradation."
""",

    # ── Slide 11: Spearman Rank Correlation & Formal Gate Decision (Fig 4) ──
    """[SPEAKING TIME: ~50 seconds]
[CUE: Refer to Figure 4 showing the correlation bars relative to the dashed GO threshold line]

"Figure 4 presents the Spearman rank correlation analysis evaluating whether our predicted sensitivity scores correlate monotonically with measured accuracy drops:

We use Spearman's rank correlation because neural network degradation is non-linear—we care about the correct ranking order, not a strict linear fit.

Look at the contrast between the red bars (TRUNC=4) and green bars (TRUNC=6):
At TRUNC=4, all metrics yielded |rho| <= 0.40, falling squarely in the red NO-GO zone due to the noise floor we just discussed.

However, at TRUNC=6, our proposed combined metric, S3, achieves a Spearman |rho| of 0.80, shown by the green bar well above the navy dashed line. This comfortably clears our strict pre-defined GO gate threshold of |rho| >= 0.70.

This empirical result validated our core research hypothesis and provided the formal justification to proceed with NSGA-II benchmarking and FPGA hardware synthesis."
""",

    # ── Slide 12: NSGA-II Optimization & Pareto Comparison (Fig 5) ─────────
    """[SPEAKING TIME: ~60 seconds]
[CUE: Point to the green star at the Pareto knee in Figure 5 and the inset search time chart]

"Slide 12 demonstrates the primary computational advantage of our work, benchmarking our single-pass method against an exhaustive 256-configuration NSGA-II evolutionary search.

In Figure 5, the blue line represents the true Pareto front optimizing two objectives simultaneously: minimizing classification accuracy loss and minimizing MAC-weighted LUT cost.

Now, observe where our proposed sensitivity-guided configuration lands—marked by the large green star:
It lands directly at the Pareto-optimal knee! It achieves 84.02% accuracy with a hardware cost of only 57.2 LUTs, achieving the ideal trade-off between accuracy and silicon area.

Now, look at the inset chart in the top right comparing search time:
ALWANN required 7.5 CPU-days—over 10,800 minutes—of genetic algorithm search to discover its Pareto front. Our NSGA-II baseline took approximately 30 minutes on local CPU.
Our proposed sensitivity probe computed the optimal configuration in just 0.2 seconds—representing a greater than 3,000,000x speedup over genetic search, while achieving the exact same Pareto-optimal quality."
""",

    # ── Slide 13: Hardware Savings & Resource Allocation (Fig 6) ───────────
    """[SPEAKING TIME: ~50 seconds]
[CUE: Point to Figure 6, highlighting the bars against the dashed MAC share curve]

"Figure 6 illustrates the silicon area return on investment achieved by our heterogeneous allocation strategy:

The bars show the LUT count per multiplier: conv1 uses 68 LUTs (Exact), while conv2, conv3, and conv4 use 46 LUTs (a 32.4% reduction). The dashed navy curve shows the MAC share of each layer.

Notice the engineering strategy here:
conv1 is protected with an Exact multiplier (68 LUTs). Because conv1 accounts for only 3.0% of total network MACs, approximating it would save negligible chip area while risking catastrophic accuracy collapse.

Now look at conv4: it accounts for 48.5% of total MAC operations. By assigning Truncated-6 to conv4, we cut multiplier area by 32.4% across nearly half the entire network's compute engine, maximizing overall dynamic power and area savings.

Overall, our heterogeneous mapping reduces multiplier LUT requirements by up to 32.4% while maintaining 84%+ classification accuracy."
""",

    # ── Slide 14: FPGA Accelerator RTL Microarchitecture ────────────────────
    """[SPEAKING TIME: ~50 seconds]
[CUE: Refer to the RTL module hierarchy on the left and the verification table on the right]

"Slide 14 details our hardware microarchitecture implemented in synthesizable Verilog in the rtl/ directory:

The accelerator hierarchy consists of:
1. cnn_accelerator_top.v: Top-level module providing AXI4-Stream slave and master ports for DMA interfacing.
2. layer_controller.v: Hardware mode decoder that reads a 2-bit layer_id register and drives mode[1:0] (00=Exact, 01=Trunc, 10=Comp).
3. conv_pe.v: The Processing Element containing an FSM that accumulates 9xCin MACs per output pixel.
4. mac_unit.v: Handles sign-magnitude math, dynamically adding or subtracting the unsigned multiplier product.
5. axm_8x8.v: Our unified multi-mode 8x8 approximate multiplier parameterized to T=6.

On the right, you can see our exhaustive verification results from verify_rtl_logic.py:
We tested all 65,536 input combinations across all four operational modes—totaling 262,144 test vectors. All 262,144 tests passed with zero mismatches against our golden mathematical model, confirming that our RTL is 100% functionally verified."
""",

    # ── Slide 15: Vivado Block Design & PYNQ-Z2 Deployment ──────────────────
    """[SPEAKING TIME: ~50 seconds]

"Slide 15 illustrates our system integration on the Xilinx Zynq-7020 SoC of the PYNQ-Z2 board:

We employ a heterogeneous hardware-software partitioning:
The Processing System (PS) runs embedded Linux on a dual ARM Cortex-A9 processor, managing image ingestion, quantization scaling, layer sequencing, and the fully connected layers.
The Programmable Logic (PL) houses our CNN Accelerator IP core clocked at 100 MHz, dedicated to accelerating the compute-intensive 3x3 convolutions.

Data streaming is managed by an AXI DMA controller over high-performance HP0 ports:
The MM2S channel streams packed 17-bit beats containing weight sign, weight magnitude, and activation pixels directly from DDR3 memory to the accelerator. The S2MM channel returns accumulated 32-bit pixel sums back to memory without CPU overhead.

Everything is automated: vivado_block_design.tcl generates the bitstream, and pynq_inference.py together with our Jupyter notebook provides on-board inference telemetry."
""",

    # ── Slide 16: Comprehensive Work Completed Summary ──────────────────────
    """[SPEAKING TIME: ~45 seconds]
[CUE: Walk through the phased status table, emphasizing that Phases 0 through 6 are fully complete]

"This table summarizes the comprehensive progress achieved across all project phases to date:

Phases 0 and 0b completed our RTL multiplier library characterization and baseline INT8 CNN quantization.
Phase 1 computed our sensitivity scores, establishing that conv1 is critical and conv4 is resilient.
Phases 2 and 2b diagnosed the TRUNC=4 noise boundary and cleared the TRUNC=6 GO gate with |rho| = 0.80.
Phase 3 completed our NSGA-II Pareto optimization, confirming our 0.2-second knee alignment.
Phase 4 completed the synthesizable Verilog accelerator, verified across 262,144 test vectors.
Phases 5 and 6 delivered our Vivado block design scripts, extracted INT8 weights, and PYNQ-Z2 Jupyter deployment drivers.

All code, RTL, datasets, and documentation are version-controlled in Git and prepared for publication."
""",

    # ── Slide 17: Individual Contributions & Responsibilities ──────────────
    """[SPEAKING TIME: ~40 seconds]

"Technical responsibilities were distributed across our four team members according to core specializations:

Velivala Keerthi led the RTL approximate multiplier design, exhaustive 65,536-pair simulations, and the Processing Element datapath, authoring the 262k vector verification suite.
T. Venkata Ram Charan Reddy led CNN baseline modeling, INT8 quantization, sensitivity metric formulation, noise floor diagnosis, and correlation gate validation.
Shaik Hanifa formulated and executed the NSGA-II multi-objective genetic algorithm in Python, extracting the Pareto front and verifying our knee alignment.
K. Dinesh architected the Vivado system block design, AXI DMA interfacing, Zynq PS/PL partitioning, and the PYNQ-Z2 on-board Python drivers."
""",

    # ── Slide 18: Project Timeline & Upcoming Milestones ────────────────────
    """[SPEAKING TIME: ~40 seconds]

"Slide 18 presents our 12-week project roadmap:

Weeks 1 through 8 have successfully delivered the entire algorithmic, optimization, RTL, and simulation pipeline.

Our upcoming milestones for Weeks 9 through 12 are:
In Week 9, executing vivado_block_design.tcl in Vivado on PC to compile the physical bitstream (cnn_axm.bit).
In Week 10, flashing the bitstream onto our physical PYNQ-Z2 board to measure hardware wall-clock latency, throughput in FPS, and on-chip power dissipation.
In Weeks 11 and 12, incorporating the physical board telemetry into our 6-page IEEE manuscript draft and submitting to our target conference.

Our primary targets are Scopus-indexed IEEE conferences—such as IEEE ISVLSI or IEEE ICECCT—with IEEE Access targeted for an extended journal publication."
""",

    # ── Slide 19: Conclusion & Key Scientific Findings ──────────────────────
    """[SPEAKING TIME: ~45 seconds]

"In conclusion, this project delivers five defensible, scientifically validated contributions:

First, at the circuit level, we proved that Compensated multipliers strictly dominate Truncated designs, achieving a 35% error reduction at zero additional LUT overhead.
Second, we demonstrated a single-pass sensitivity metric combining weight variance and loss gradients that maps layers in 0.2 seconds without retraining.
Third, we uncovered the asymmetric computational payoff of deep layers, showing that conv4 executes 48.5% of total MACs with near-zero error sensitivity.
Fourth, our NSGA-II benchmark confirmed that our sensitivity assignment matches the Pareto knee at a >3,000,000x search speedup over ALWANN.
Finally, we realized and verified a complete synthesizable RTL accelerator with AXI DMA streaming, ready for physical PYNQ-Z2 deployment."
""",

    # ── Slide 20: Bibliographic References ──────────────────────────────────
    """[SPEAKING TIME: ~20 seconds]

"These references represent foundational literature in approximate computing and neural network acceleration that directly informed our design methodology and comparative benchmarks.

Thank you very much for your time and attention. We are now open for your questions and valuable feedback."
"""
]

print("Applying speaker notes to all 20 slides...")
for idx, note_text in enumerate(NOTES):
    slide = prs.slides[idx]
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = note_text.strip()
    print(f"  Slide {idx+1:2d}: Notes added ({len(note_text.splitlines())} lines)")

prs.save(PPT_OUTPUT)
print("=" * 60)
print(f"All speaker notes successfully embedded into: {PPT_OUTPUT}")
print("=" * 60)
