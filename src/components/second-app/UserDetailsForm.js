// src/components/UserDetailsForm.js
import { useState, useEffect } from 'react';
import './UserDetailsForm.css';

const UserDetailsForm = ({ onSave, initialData }) => {
    const [formData, setFormData] = useState(initialData || {
        name: '',
        age: '',
        healthCondition: '',
        criminalRecord: '',
        ipcsApplied: ''
    });

    const allFieldsFilled = Object.values(formData).every(value => value.trim() !== '');

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (allFieldsFilled) {
            onSave(formData);
        }
    };

    return (
        <div className="form-overlay">
            <form className="user-details-form" onSubmit={handleSubmit}>
                <h2>User Details</h2>

                <label>
                    Full Name:
                    <input type="text" name="name" value={formData.name} onChange={handleChange} required />
                </label>

                <label>
                    Age:
                    <input type="number" name="age" value={formData.age} onChange={handleChange} min="18" required />
                </label>

                <label>
                    Health Condition:
                    <textarea name="healthCondition" value={formData.healthCondition} onChange={handleChange} required />
                </label>

                <label>
                    Past Criminal Record:
                    <select name="criminalRecord" value={formData.criminalRecord} onChange={handleChange} required>
                        <option value="">Select</option>
                        <option value="none">None</option>
                        <option value="minor">Minor</option>
                        <option value="major">Major</option>
                    </select>
                </label>

                <label>
                    IPCs Applied:
                    <input type="text" name="ipcsApplied" value={formData.ipcsApplied}
                        onChange={handleChange} required />
                </label>

                <button type="submit" disabled={!allFieldsFilled} className="submit-btn">
                    Submit Details
                </button>
            </form>
        </div>
    );
};

export default UserDetailsForm;
