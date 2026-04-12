import React, { useState } from 'react';
import '../styles/SubCompartmentInput.css';

/**
 * SubCompartmentInput Component
 * Allows users to specify compartments and sub-compartments for hierarchical division
 * Example: C1 with 8 subs, C2 with 4 subs → C1S1-C1S8, C2S1-C2S4
 */

export interface CompartmentSpec {
  compartmentNumber: number;
  subCompartmentCount: number;
}

interface SubCompartmentInputProps {
  value: CompartmentSpec[];
  onChange: (specs: CompartmentSpec[]) => void;
  disabled?: boolean;
  maxCompartments?: number;
  maxSubCompartments?: number;
}

export const SubCompartmentInput: React.FC<SubCompartmentInputProps> = ({
  value,
  onChange,
  disabled = false,
  maxCompartments = 10,
  maxSubCompartments = 20,
}) => {
  const [specs, setSpecs] = useState<CompartmentSpec[]>(
    value.length > 0 ? value : [{ compartmentNumber: 1, subCompartmentCount: 8 }]
  );

  const handleAddCompartment = () => {
    if (specs.length >= maxCompartments) {
      alert(`Maximum ${maxCompartments} compartments allowed`);
      return;
    }

    const newSpecs = [
      ...specs,
      {
        compartmentNumber: specs.length + 1,
        subCompartmentCount: 4,
      },
    ];
    setSpecs(newSpecs);
    onChange(newSpecs);
  };

  const handleRemoveCompartment = (index: number) => {
    if (specs.length <= 1) {
      alert('At least one compartment is required');
      return;
    }

    const newSpecs = specs.filter((_, i) => i !== index);
    // Renumber compartments
    const renumbered = newSpecs.map((spec, idx) => ({
      ...spec,
      compartmentNumber: idx + 1,
    }));
    setSpecs(renumbered);
    onChange(renumbered);
  };

  const handleSubCountChange = (index: number, count: number) => {
    if (count < 1 || count > maxSubCompartments) {
      return;
    }

    const newSpecs = [...specs];
    newSpecs[index].subCompartmentCount = count;
    setSpecs(newSpecs);
    onChange(newSpecs);
  };

  const getTotalSubCompartments = () => {
    return specs.reduce((sum, spec) => sum + spec.subCompartmentCount, 0);
  };

  const getPreviewLabels = (spec: CompartmentSpec): string[] => {
    const labels: string[] = [];
    for (let i = 1; i <= Math.min(spec.subCompartmentCount, 3); i++) {
      labels.push(`C${spec.compartmentNumber}S${i}`);
    }
    if (spec.subCompartmentCount > 3) {
      labels.push('...');
      labels.push(`C${spec.compartmentNumber}S${spec.subCompartmentCount}`);
    }
    return labels;
  };

  return (
    <div className="sub-compartment-input">
      <div className="input-header">
        <h3>Compartment Configuration</h3>
        <p className="help-text">
          Specify how many compartments and sub-compartments to create. Each compartment will be
          divided into equal-area sub-compartments.
        </p>
      </div>

      <div className="compartment-specs">
        {specs.map((spec, index) => (
          <div key={index} className="compartment-spec-row">
            <div className="spec-number">
              <span className="compartment-label">Compartment {spec.compartmentNumber}</span>
            </div>

            <div className="spec-input">
              <label htmlFor={`sub-count-${index}`}>Sub-compartments:</label>
              <input
                id={`sub-count-${index}`}
                type="number"
                min="1"
                max={maxSubCompartments}
                value={spec.subCompartmentCount}
                onChange={(e) => handleSubCountChange(index, parseInt(e.target.value, 10))}
                disabled={disabled}
                className="sub-count-input"
              />
            </div>

            <div className="spec-preview">
              <span className="preview-label">Labels:</span>
              <div className="preview-badges">
                {getPreviewLabels(spec).map((label, idx) => (
                  <span key={idx} className="preview-badge">
                    {label}
                  </span>
                ))}
              </div>
            </div>

            <div className="spec-actions">
              {specs.length > 1 && (
                <button
                  type="button"
                  className="btn-remove"
                  onClick={() => handleRemoveCompartment(index)}
                  disabled={disabled}
                  title="Remove compartment"
                >
                  ✕
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="input-actions">
        <button
          type="button"
          className="btn btn-secondary"
          onClick={handleAddCompartment}
          disabled={disabled || specs.length >= maxCompartments}
        >
          + Add Compartment
        </button>
      </div>

      <div className="input-summary">
        <div className="summary-item">
          <span className="summary-label">Total Compartments:</span>
          <span className="summary-value">{specs.length}</span>
        </div>
        <div className="summary-item">
          <span className="summary-label">Total Sub-compartments:</span>
          <span className="summary-value">{getTotalSubCompartments()}</span>
        </div>
      </div>

      <div className="input-info">
        <p className="info-text">
          <strong>Example:</strong> If you create 2 compartments with 4 and 8 sub-compartments,
          the system will generate labels: C1S1, C1S2, C1S3, C1S4, C2S1, C2S2, ..., C2S8
        </p>
      </div>
    </div>
  );
};

export default SubCompartmentInput;
