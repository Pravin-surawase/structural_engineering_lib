# Blog Post 02: Deterministic ML — When Classical Methods Beat Neural Networks

**Target:** Dev.to (primary), HackerNews (via submission)
**Audience:** Software engineers interested in ML alternatives, tech leads making architecture decisions
**Estimated length:** 1800-2200 words
**Publication date:** 2025-01-30
**Status:** OUTLINE

---

## Working Title

**Option 1:** "Deterministic ML: When Classical Methods Beat Neural Networks"
**Option 2:** "Why We Chose Perturbation Analysis Over Deep Learning"
**Option 3:** "The Case Against Machine Learning in Engineering Software"

**Selected:** Option 1 (balanced, not anti-ML)

---

## Hook (100 words)

**The Setup:**
> "Just use machine learning" has become the default answer to any optimization or prediction problem. But what if ML is the wrong tool for the job?

**The Contrarian View:**
For engineering problems with:
- Small datasets (10-100 examples, not 10,000)
- Physical models (equations known)
- Deterministic requirements (same input → same output)
- Safety criticality (explainability required)

Classical methods aren't just "good enough"—they're often **superior** to ML.

This post explores why, with concrete examples from structural engineering.

---

## Section 1: The ML Hammer Problem (300 words)

### When You Have a Hammer, Everything Looks Like a Nail

**Industry trend:**
- 2015-2020: "Deep learning solves everything"
- 2020-2025: Reality check (ChatGPT aside)

**Examples of ML Overuse:**
1. **Recommendation systems** — Actually need collaborative filtering, not neural nets
2. **Time series forecasting** — ARIMA often beats LSTM for small datasets
3. **Optimization** — Gradient descent when analytical solutions exist

**Why it happens:**
- ML is trendy (resumes, funding, hype)
- Classical methods seem "boring"
- Universities teach ML, not optimization theory
- Tooling is better (TensorFlow vs NumPy)

**The cost:**
- Longer development time
- Higher computational cost
- Black-box outputs (no explainability)
- Brittleness to distribution shift

**Real-world example:**
```python
# ML approach (overkill)
model = keras.Sequential([
    Dense(64, activation='relu'),
    Dense(32, activation='relu'),
    Dense(1)
])
model.fit(X_train, y_train, epochs=100)  # Hours of training

# Classical approach (sufficient)
from scipy.optimize import minimize
result = minimize(objective, x0, constraints=constraints)  # Seconds
```

---

## Section 2: Problem Characteristics Matrix (400 words)

### When to Use ML vs Classical Methods

**Decision matrix:**

| Characteristic | ML Better | Classical Better |
|----------------|-----------|------------------|
| Dataset size | >1000 samples | <100 samples |
| Physical model | Unknown/complex | Known/tractable |
| Explainability | Not required | Critical |
| Determinism | Stochastic OK | Repeatability required |
| Compute budget | High (GPUs) | Low (CPU) |
| Safety criticality | Low | High |
| Regulatory approval | Not required | Required (FDA, codes) |

**Engineering software characteristics:**

| Factor | Structural Engineering | Typical ML Use Case |
|--------|------------------------|---------------------|
| Data | 10-15 verified examples | 10,000+ training samples |
| Model | IS 456 equations | Pattern recognition |
| Output | Must cite clauses | Probabilistic predictions |
| Validation | 100% accuracy required | 95% accuracy acceptable |
| Explainability | Mandatory | Nice-to-have |
| Cost of error | Structural failure | Annoying prediction |

**Verdict: Classical methods are the right tool.**

### Categories of Classical Methods

**1. Optimization**
- Linear programming (simplex)
- Quadratic programming
- Evolutionary algorithms (deterministic with seed)
- Gradient-free (Nelder-Mead, Powell)

**2. Sensitivity Analysis**
- Finite differences (perturbation)
- Adjoint methods (efficient gradients)
- Sobol indices (variance decomposition)

**3. Heuristics**
- Rules of thumb (engineering practice)
- Expert systems (if-then rules)
- Constraint propagation

**4. Surrogates**
- Polynomial response surfaces
- Gaussian processes (kriging)
- Radial basis functions

**All are:**
- ✅ Deterministic (repeatable)
- ✅ Explainable (traceable)
- ✅ Efficient (small data)

---

## Section 3: Case Study — Sensitivity Analysis (500 words)

### Problem: Which Parameters Are Critical?

**Engineering context:**
A beam has 6 design parameters (width, depth, span, loads, materials). Which ones matter most for safety?

**ML approach (over-engineered):**

```python
# Train a neural network to predict utilization
import tensorflow as tf

model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu', input_shape=(6,)),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(1)
])

# Generate 1000 training samples
X_train, y_train = generate_training_data(n=1000)  # Hours of simulation

# Train
model.fit(X_train, y_train, epochs=50, batch_size=32)  # 10-20 minutes

# Extract feature importance (SHAP, LIME)
import shap
explainer = shap.Explainer(model, X_train)
shap_values = explainer(X_test)  # More computation

# Result: "Depth is important" (no quantification, no determinism)
```

**Problems:**
- ❌ Requires 1000+ samples (expensive to generate)
- ❌ Training time: 10-20 minutes
- ❌ Non-deterministic (different runs → different results)
- ❌ Explainability via SHAP (approximation, not exact)
- ❌ Can't cite in code compliance report

**Classical approach (perturbation analysis):**

```python
def sensitivity_analysis(base_params, perturbation=0.10):
    """Deterministic sensitivity via finite differences."""
    base_result = design_function(**base_params)
    base_utilization = base_result.utilization

    sensitivities = {}

    for param in base_params.keys():
        # Perturb +10%
        perturbed_params = base_params.copy()
        perturbed_params[param] *= (1 + perturbation)

        # Evaluate
        perturbed_result = design_function(**perturbed_params)
        perturbed_utilization = perturbed_result.utilization

        # Sensitivity (% change in output / % change in input)
        delta = (perturbed_utilization - base_utilization) / base_utilization
        sensitivities[param] = delta / perturbation

    return sorted(sensitivities.items(), key=lambda x: abs(x[1]), reverse=True)

# Usage
result = sensitivity_analysis({
    'd': 450, 'b': 300, 'span': 5000,
    'mu': 120, 'fck': 25, 'fy': 500
})

# Output:
# [
#   ('d', -0.24),      # 10% depth increase → 2.4% util decrease
#   ('mu', +0.14),     # 10% moment increase → 1.4% util increase
#   ('b', -0.13),      # 10% width increase → 1.3% util decrease
#   ...
# ]
```

**Advantages:**
- ✅ Zero training data needed
- ✅ Execution time: ~50ms (6 parameters × ~8ms per design)
- ✅ 100% deterministic
- ✅ Exact quantification (not approximation)
- ✅ Physically interpretable (depth > width makes sense)
- ✅ Can cite in compliance reports

**Comparison:**

| Metric | ML Approach | Classical Approach |
|--------|-------------|---------------------|
| Training samples | 1000+ | 0 |
| Computation time | 10-20 min | 50 ms |
| Deterministic | No | Yes |
| Explainability | SHAP (approx) | Exact derivatives |
| Regulatory compliant | No | Yes |

**Winner: Classical (100x faster, deterministic, compliant)**

---

## Section 4: Case Study — Predictive Validation (400 words)

### Problem: Quick Pre-Checks Before Full Design

**ML approach (overkill):**

Train a classifier to predict "will this design fail?"

```python
# Collect 500+ design attempts with pass/fail labels
X_train = [...]  # (span, b, d, mu, fck, fy)
y_train = [...]  # (0=fail, 1=pass)

# Train classifier
from sklearn.ensemble import RandomForestClassifier
clf = RandomForestClassifier(n_estimators=100)
clf.fit(X_train, y_train)

# Predict
prediction = clf.predict([[5000, 300, 450, 120, 25, 500]])
# Output: [1] → "Probably passes" (no explanation, ~95% confidence)
```

**Problems:**
- ❌ Needs 500+ training examples
- ❌ Probabilistic (95% confident ≠ certain)
- ❌ No actionable feedback ("increase d" not provided)
- ❌ Retraining required when code changes

**Classical approach (heuristic rules):**

```python
def quick_precheck(span_mm, b_mm, d_mm, mu_knm, fck_nmm2, fy_nmm2):
    """Heuristic validation from IS 456 and practice."""
    warnings = []

    # Rule 1: Span/depth ratio (Table 23)
    if span_mm / d_mm > 20:
        warnings.append({
            'rule': 'Deflection check',
            'issue': f'Span/d = {span_mm/d_mm:.1f} > 20',
            'fix': f'Increase d to {span_mm/18:.0f}mm',
            'basis': 'IS 456 Table 23'
        })

    # Rule 2: Steel estimate (lever arm = 0.9d)
    ast_est = (mu_knm * 1e6) / (0.87 * fy_nmm2 * 0.9 * d_mm)
    pt_est = ast_est / (b_mm * d_mm) * 100

    if pt_est > 4.0:
        warnings.append({
            'rule': 'Reinforcement limit',
            'issue': f'Est. steel % = {pt_est:.2f}% > 4%',
            'fix': 'Increase depth or use doubly reinforced',
            'basis': 'Singly-reinforced economical up to ~4%'
        })

    return warnings

# Usage
warnings = quick_precheck(5000, 300, 450, 120, 25, 500)
# Output: [] (clean) or detailed actionable warnings
```

**Advantages:**
- ✅ Zero training data
- ✅ Execution: <1ms (instant)
- ✅ 100% deterministic
- ✅ Actionable fixes provided
- ✅ Clause references for traceability

**Winner: Classical (instant, actionable, compliant)**

---

## Section 5: When ML Actually Helps (250 words)

### Not Anti-ML, Just Pro-Right-Tool

**ML is genuinely better for:**

1. **Pattern recognition** (images, audio, text)
   - Example: Crack detection in concrete from photos
   - Why ML: Visual patterns hard to codify

2. **Complex non-linear relationships** (when physical model unknown)
   - Example: Predicting construction delays from project data
   - Why ML: 100+ interacting factors, no equation

3. **Large-scale data** (when you have 10,000+ samples)
   - Example: Predictive maintenance from sensor streams
   - Why ML: Data-rich, pattern-rich

4. **User behavior** (non-deterministic by nature)
   - Example: Material ordering patterns
   - Why ML: Human behavior is stochastic

**Hybrid approach (best of both):**

```python
# Use ML where it helps
crack_detected = cnn_model.predict(beam_photo)  # Image recognition

# Use classical where it's better
if crack_detected:
    sensitivity = perturbation_analysis(beam_params)  # Deterministic
    recommendation = optimize_repair(sensitivity)      # Gradient-free
```

**Guideline:**
- Physical model known → Classical
- Physical model unknown + large data → ML
- Safety-critical → Classical (explainability)
- Nice-to-have → ML acceptable

---

## Section 6: Implementation Lessons (300 words)

### How to Choose the Right Method

**Decision tree:**

```
START: Do you have a physical/mathematical model?
├─ YES: Do you need 100% determinism?
│  ├─ YES: Use classical methods
│  └─ NO: Do you have >1000 samples?
│     ├─ YES: Consider ML (if it improves accuracy)
│     └─ NO: Use classical methods
└─ NO: Do you have >1000 labeled samples?
   ├─ YES: Use ML
   └─ NO: Collect more data OR use heuristics
```

**Implementation tips:**

1. **Start with the simplest method**
   - Linear regression before neural nets
   - Finite differences before adjoint methods
   - Rules of thumb before optimization

2. **Benchmark against classical baselines**
   - If ML doesn't beat linear regression by >10%, use linear regression
   - Complexity must justify gains

3. **Measure what matters**
   - Determinism (repeatability)
   - Explainability (traceability)
   - Performance (latency)
   - Not just "accuracy"

4. **Document your assumptions**
   - "Sensitivity assumes local linearity (±10%)"
   - "Heuristics based on IS 456 Table 23"
   - Transparency > black-box accuracy

**Red flags for ML:**
- ❌ "We'll need to collect 10,000 samples"
- ❌ "It's probabilistic, not deterministic"
- ❌ "We can't explain why it works"
- ❌ "Training takes 4 hours on GPUs"

---

## Section 7: The Validation Story (200 words)

### How We Knew Classical Methods Worked

**Test methodology:**
- Golden vectors from IS 456 worked examples
- 3 verified test cases (light/typical/heavy steel)
- 100% accuracy required (no "95% is good enough")

**Results:**

| Method | Samples | Accuracy | Time | Deterministic |
|--------|---------|----------|------|---------------|
| Sensitivity Analysis | 3 | 100% | 50ms | ✅ Yes |
| Predictive Validation | 4 | 100% | <1ms | ✅ Yes |
| Constructability | 3 | 100% | <1ms | ✅ Yes |

**Key insight:**
Small data (3-4 cases) sufficient when:
- Physical model is correct (IS 456 equations validated over decades)
- Test cases are representative (light/typical/heavy covers range)
- Method is deterministic (no randomness to average out)

**Contrast with ML:**
- Would need 100-1000 samples
- 95% accuracy considered good
- Non-deterministic (average over runs)

**Lesson: Right tool → right sample size.**

---

## Section 8: Key Takeaways (200 words)

### What Software Engineers Should Remember

**1. Question the ML Default**
- "Should we use ML?" → "What's the classical baseline?"
- ML is powerful, not universal

**2. Small Data ≠ Use ML**
- ML needs 1000+ samples
- Classical methods work with 10-100
- Physical models are data-efficient

**3. Determinism Matters**
- Engineering: same input → same output
- Finance: same trade → same price
- Healthcare: same diagnosis → same recommendation
- ML's stochasticity is a bug, not a feature

**4. Explainability Isn't Optional**
- Regulatory approval requires it
- Engineers need to cite clauses
- SHAP/LIME are approximations

**5. Boring Tech Wins**
- Finite differences (1960s) > neural nets (2010s) for sensitivity
- Linear programming (1940s) > GANs (2014) for optimization
- Rules of thumb (centuries) > deep learning for validation

**The best code is the code that works, not the code that's trendy.**

---

## Call to Action (100 words)

**Try it yourself:**

Compare classical vs ML for your next problem:

```python
# Baseline: Classical method
baseline = simple_optimization(objective, x0)

# Challenger: ML method
ml_result = neural_network_approach(X_train, y_train)

# Compare:
# - Sample requirements
# - Computation time
# - Determinism
# - Explainability

# Be honest: Does ML actually win?
```

**Read more:**
- [Optimization without ML: A Practical Guide](...)
- [When to NOT Use Machine Learning](...)

**Discuss:** What classical methods have you used successfully?

---

## Metadata

**Tags:** #machine-learning #optimization #classical-methods #engineering #determinism #software-architecture
**Estimated reading time:** 9 minutes
**Controversial meter:** 🔥🔥 (medium-hot take)
**Target audience:** Intermediate-senior developers
**Prerequisites:** Basic understanding of ML and optimization

---

**Draft status:** OUTLINE COMPLETE
**Next steps:**
1. Expand with more code examples
2. Add performance benchmarks
3. Add decision tree diagram
4. Internal review
5. Publish to Dev.to
6. Submit to HackerNews
