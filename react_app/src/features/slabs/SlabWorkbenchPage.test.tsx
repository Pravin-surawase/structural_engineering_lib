import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { SlabWorkbenchPage } from './SlabWorkbenchPage';

const { designSlabWorkflowMock } = vi.hoisted(() => ({
  designSlabWorkflowMock: vi.fn(),
}));

vi.mock('./client', () => ({
  designSlabWorkflow: designSlabWorkflowMock,
}));

function region(adequate = true) {
  return {
    area_passed: adequate,
    diameter_passed: true,
    spacing_passed: true,
  };
}

function passingContinuousResult() {
  return {
    flexure: {
      input: {
        coefficients: {
          method: 'built_in_exact',
          table_id: 'IS456_TABLE_12_13',
          case_id: 'end_span_positive|next_to_end_support_negative|end_support',
          source_reference: 'IS456_TABLE_12_13',
        },
      },
      positive_midspan: { factored_moment_knm_per_m: 10.6875 },
      negative_support: { factored_moment_knm_per_m: 12.825 },
    },
    positive_reinforcement: region(),
    negative_reinforcement: region(),
    distribution_reinforcement: region(),
    shear: {
      tau_v_n_per_mm2: 0.148,
      status: 'concrete_capacity_satisfied',
      shear_reinforcement_design_status: 'not_automatically_designed',
    },
    punching_shear_disposition: 'not_applicable_to_supported_beam_or_wall_supported_udl_panel',
    serviceability: {
      utilization: 0.94,
      status: 'satisfied_with_reviewed_limit',
      direct_deflection_status: 'held_not_implemented',
    },
  };
}

function passingTwoWayResult({
  tableId = 'IS456_TABLE_26',
  caseId = 'table_26_case_4',
  torsionClass = 'full',
}: {
  tableId?: string;
  caseId?: string;
  torsionClass?: string;
} = {}) {
  const corners = ['x_min_y_min', 'x_min_y_max', 'x_max_y_min', 'x_max_y_max'];
  return {
    panel: {
      input: {
        coefficients: {
          method: 'built_in_exact',
          table_id: tableId,
          case_id: caseId,
          source_reference: tableId,
          aspect_ratio_ly_lx: 1.5,
          interpolation_bounds: [1.5, 1.5],
        },
      },
      x_negative: {
        factored_moment_knm_per_m: tableId === 'IS456_TABLE_27' ? 0 : 18.6,
        reinforcement: region(),
      },
      x_positive: { factored_moment_knm_per_m: 13.888, reinforcement: region() },
      y_negative: {
        factored_moment_knm_per_m: tableId === 'IS456_TABLE_27' ? 0 : 11.656,
        reinforcement: region(),
      },
      y_positive: { factored_moment_knm_per_m: 8.68, reinforcement: region() },
      edge_strip_reinforcement: region(),
      strip_distribution: {
        x_moment_middle_strip_width_mm: 4500,
        x_moment_edge_strip_width_each_mm: 750,
        y_moment_middle_strip_width_mm: 3000,
        y_moment_edge_strip_width_each_mm: 500,
      },
      corner_torsion: corners.map((corner) => ({
        corner,
        torsion_class: torsionClass,
        zone_extent_from_each_edge_mm: 800,
        required_each_of_four_layers_mm2_per_m: torsionClass === 'full' ? 150 : 0,
        provided_each_layer_mm2_per_m: 251.3,
        is_adequate: true,
      })),
      shear: {
        tau_v_n_per_mm2: 0.248,
        status: 'concrete_capacity_satisfied',
        shear_reinforcement_design_status: 'not_automatically_designed',
      },
      punching_shear_disposition: 'not_applicable_to_supported_beam_or_wall_supported_udl_panel',
      held_scope: [
        'Direct deflection and crack-width calculations are held.',
        'Automatic slab shear reinforcement design is held.',
        'Flat slabs, drops, column strips, and punching shear require separate approval.',
      ],
    },
    serviceability: {
      utilization: 0.89,
      status: 'satisfied_with_reviewed_limit',
      direct_deflection_status: 'held_not_implemented',
    },
  };
}

describe('SlabWorkbenchPage', () => {
  beforeEach(() => designSlabWorkflowMock.mockReset());

  it('runs B02 with selectable action locations and invalidates a stale passport', async () => {
    designSlabWorkflowMock.mockResolvedValue(passingContinuousResult());

    render(<SlabWorkbenchPage />);

    fireEvent.change(screen.getByRole('combobox', { name: /positive action location/i }), {
      target: { value: 'interior_span_positive' },
    });
    fireEvent.click(screen.getByRole('button', { name: /run slab design/i }));

    expect(await screen.findByText('10.688')).toBeInTheDocument();
    expect(screen.getByText(/is456_table_12_13 · built_in_exact/i)).toBeInTheDocument();
    expect(screen.getByText('Bounded checks satisfied')).toBeInTheDocument();
    expect(designSlabWorkflowMock).toHaveBeenCalledWith(
      'continuous',
      expect.objectContaining({
        number_of_spans: 3,
        positive_location: 'interior_span_positive',
      }),
      expect.any(AbortSignal),
    );

    const download = screen.getByRole('button', { name: /download passport/i });
    expect(download).toBeEnabled();
    fireEvent.change(screen.getByRole('spinbutton', { name: /effective span/i }), {
      target: { value: '3200' },
    });
    expect(screen.getByText(/inputs changed after this response/i)).toBeInTheDocument();
    expect(screen.getByText('stale')).toBeInTheDocument();
    expect(download).toBeDisabled();
  });

  it('renders the B04 provenance, strips, torsion and returned dispositions', async () => {
    designSlabWorkflowMock.mockResolvedValue(passingTwoWayResult());
    render(<SlabWorkbenchPage />);

    fireEvent.click(screen.getByRole('button', { name: /two-way panel/i }));
    fireEvent.click(screen.getByRole('button', { name: /run slab design/i }));

    expect(await screen.findByText('table_26_case_4')).toBeInTheDocument();
    expect(screen.getByText('4500.0 mm')).toBeInTheDocument();
    expect(screen.getByText('Per-corner torsion schedule')).toBeInTheDocument();
    expect(screen.getAllByText(/full · adequate/i)).toHaveLength(4);
    expect(screen.getByText('Punching shear boundary')).toBeInTheDocument();
    expect(screen.getByText('not applicable to supported beam or wall supported udl panel')).toBeInTheDocument();
    expect(screen.getByText('Bounded checks satisfied')).toBeInTheDocument();
    expect(screen.getByText(/direct deflection and crack-width calculations are held/i)).toBeInTheDocument();
  });

  it('selects the Table 27 free-corner route and sends four discontinuous edges', async () => {
    designSlabWorkflowMock.mockResolvedValue(
      passingTwoWayResult({
        tableId: 'IS456_TABLE_27',
        caseId: 'simply_supported_four_sides_corners_free',
        torsionClass: 'not_applicable_free_to_lift',
      }),
    );
    render(<SlabWorkbenchPage />);

    fireEvent.click(screen.getByRole('button', { name: /two-way panel/i }));
    fireEvent.change(screen.getByRole('combobox', { name: /corner lift condition/i }), {
      target: { value: 'free_to_lift' },
    });
    expect(screen.getByRole('combobox', { name: /x-max edge/i })).toHaveValue('discontinuous');
    expect(screen.getByRole('combobox', { name: /y-max edge/i })).toHaveValue('discontinuous');
    fireEvent.click(screen.getByRole('button', { name: /run slab design/i }));

    expect(await screen.findByText('simply_supported_four_sides_corners_free')).toBeInTheDocument();
    expect(screen.getAllByText(/not applicable free to lift · adequate/i)).toHaveLength(4);
    expect(designSlabWorkflowMock).toHaveBeenCalledWith(
      'two-way',
      expect.objectContaining({
        x_min_edge: 'discontinuous',
        x_max_edge: 'discontinuous',
        y_min_edge: 'discontinuous',
        y_max_edge: 'discontinuous',
        corner_lift_condition: 'free_to_lift',
      }),
      expect.any(AbortSignal),
    );
  });

  it('supports another restrained topology through physical edge controls', async () => {
    designSlabWorkflowMock.mockResolvedValue(
      passingTwoWayResult({ caseId: 'table_26_case_1', torsionClass: 'none' }),
    );
    render(<SlabWorkbenchPage />);

    fireEvent.click(screen.getByRole('button', { name: /two-way panel/i }));
    fireEvent.change(screen.getByRole('combobox', { name: /x-min edge/i }), {
      target: { value: 'continuous' },
    });
    fireEvent.change(screen.getByRole('combobox', { name: /y-min edge/i }), {
      target: { value: 'continuous' },
    });
    fireEvent.click(screen.getByRole('button', { name: /run slab design/i }));

    expect(await screen.findByText('table_26_case_1')).toBeInTheDocument();
    expect(designSlabWorkflowMock).toHaveBeenCalledWith(
      'two-way',
      expect.objectContaining({
        x_min_edge: 'continuous',
        x_max_edge: 'continuous',
        y_min_edge: 'continuous',
        y_max_edge: 'continuous',
        corner_lift_condition: 'restrained',
      }),
      expect.any(AbortSignal),
    );
  });

  it('surfaces inadequate reinforcement and review-required outcomes', async () => {
    designSlabWorkflowMock.mockResolvedValue({
      reinforcement: {
        flexure: {
          factored_moment_knm: 11.25,
          limitations: ['HOLD: load combinations are not inferred.'],
        },
        detailing: {
          detailing_adequacy: 'inadequate',
          limitations: ['HOLD: direct deflection is not implemented.'],
        },
      },
      shear: {
        tau_v_n_per_mm2: 0.91,
        status: 'increase_depth_or_engineer_reinforcement',
        shear_reinforcement_design_status: 'not_automatically_designed',
      },
      punching_shear_disposition: 'not_applicable_to_supported_beam_or_wall_supported_udl_panel',
      serviceability: {
        utilization: 1.18,
        status: 'limit_exceeded',
        direct_deflection_status: 'held_not_implemented',
      },
    });
    render(<SlabWorkbenchPage />);

    fireEvent.click(screen.getByRole('button', { name: /one-way simple/i }));
    fireEvent.click(screen.getByRole('button', { name: /run slab design/i }));

    expect(await screen.findByText('Redesign or qualified review required')).toBeInTheDocument();
    expect(screen.getByText('inadequate')).toBeInTheDocument();
    expect(screen.getByText('increase depth or engineer reinforcement')).toBeInTheDocument();
    expect(screen.getByText('limit exceeded')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /download passport/i })).toBeEnabled();
  });
});
