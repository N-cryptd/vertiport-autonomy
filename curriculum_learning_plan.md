# Curriculum Learning Plan for Vertiport Autonomy

## Problem Diagnosis
The PPO_Vertiport_5 agent is failing to learn due to:
- **Immediate episode termination** (ep_len_mean = 1)
- **Catastrophic penalties** (-5000 for unauthorized landing)
- **Zero variance in outcomes** (explained_variance = NaN)
- **Flat loss curves** indicating no policy updates

## Curriculum Learning Strategy

### Phase 1: "Easy World" (Basic Navigation)
**Objective**: Learn fundamental navigation and mission completion

**Environment Modifications**:
- Disable unauthorized landing penalty (-5000 → 0)
- Reduce collision penalty (-1000 → -10)
- Reduce LoS penalty (dense → minimal)
- Add positive progress rewards
- Increase arrival radius for easier waypoint reaching

**Expected Outcome**: Agent learns basic flight patterns and mission flow

### Phase 2: "Intermediate World" (Safety Awareness)
**Objective**: Introduce safety constraints gradually

**Environment Modifications**:
- Enable moderate collision penalty (-1000 → -100)
- Enable basic LoS penalties
- Keep unauthorized landing penalty disabled
- Maintain some progress rewards

**Expected Outcome**: Agent learns collision avoidance while maintaining mission capability

### Phase 3: "Hard World" (Full SRS Compliance)
**Objective**: Full regulatory compliance with all penalties

**Environment Modifications**:
- Full collision penalty (-1000)
- Full unauthorized landing penalty (-5000)
- Complete LoS penalty system
- Remove training wheels

**Expected Outcome**: Fully compliant autonomous vertiport operations

## Implementation Plan

### 1. Create Curriculum Scenarios
- `scenarios/easy_world.yaml` - Phase 1 configuration
- `scenarios/intermediate_world.yaml` - Phase 2 configuration
- `scenarios/hard_world.yaml` - Phase 3 configuration (current steady_flow.yaml)

### 2. Implement Reward Shaping
- Add `curriculum_level` parameter to environment
- Implement progressive penalty scaling
- Add potential-based progress rewards for Phase 1

### 3. Create Curriculum Training Script
- `train_curriculum.py` - Automated 3-phase training
- Automatic progression criteria
- Model checkpointing between phases

### 4. Hyperparameter Adjustments
- Increase `ent_coef` for Phase 1 exploration (0.01 → 0.02)
- Longer training per phase for stability
- Learning rate scheduling

## Success Metrics
- **Phase 1**: ep_rew_mean > -50, ep_len_mean > 50
- **Phase 2**: ep_rew_mean > -200, collision rate < 10%
- **Phase 3**: ep_rew_mean > -100, full regulatory compliance

## Implementation Priority
1. Create curriculum reward system
2. Build easy world scenario
3. Implement curriculum training script
4. Test and validate progression