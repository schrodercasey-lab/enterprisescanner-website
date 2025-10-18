/**
 * Enhanced Form Validation - Phase 2
 * Enterprise Scanner Website
 * Features: Real-time validation, visual feedback, accessibility, custom rules
 */

class EnhancedFormValidation {
    constructor(options = {}) {
        this.options = {
            validateOnInput: options.validateOnInput !== false,
            validateOnBlur: options.validateOnBlur !== false,
            showSuccessStates: options.showSuccessStates !== false,
            scrollToError: options.scrollToError !== false,
            ...options
        };

        this.forms = new Map();
        this.validators = this.createValidators();
        this.init();
    }

    init() {
        this.injectStyles();
        this.registerForms();
    }

    injectStyles() {
        if (document.getElementById('enhanced-form-validation-styles')) return;

        const style = document.createElement('style');
        style.id = 'enhanced-form-validation-styles';
        style.textContent = `
            .form-group-enhanced {
                position: relative;
                margin-bottom: 1.5rem;
            }

            .form-control-enhanced {
                width: 100%;
                padding: 14px 16px 14px 48px;
                background: rgba(30, 41, 59, 0.6);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                color: #ffffff;
                font-size: 1rem;
                transition: all 0.3s ease;
                outline: none;
            }

            .form-control-enhanced:focus {
                background: rgba(30, 41, 59, 0.8);
                border-color: #3b82f6;
                box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
            }

            .form-control-enhanced.is-valid {
                border-color: #10b981;
                background: rgba(16, 185, 129, 0.05);
            }

            .form-control-enhanced.is-invalid {
                border-color: #ef4444;
                background: rgba(239, 68, 68, 0.05);
            }

            .form-icon {
                position: absolute;
                left: 16px;
                top: 50%;
                transform: translateY(-50%);
                color: rgba(255, 255, 255, 0.4);
                font-size: 1.2rem;
                transition: all 0.3s ease;
                pointer-events: none;
            }

            .form-control-enhanced:focus + .form-icon {
                color: #3b82f6;
            }

            .form-control-enhanced.is-valid + .form-icon {
                color: #10b981;
            }

            .form-control-enhanced.is-invalid + .form-icon {
                color: #ef4444;
            }

            .form-label-enhanced {
                display: block;
                margin-bottom: 8px;
                color: rgba(255, 255, 255, 0.8);
                font-weight: 500;
                font-size: 0.95rem;
            }

            .form-label-required::after {
                content: '*';
                color: #ef4444;
                margin-left: 4px;
            }

            .form-feedback {
                display: none;
                margin-top: 8px;
                font-size: 0.875rem;
                padding-left: 48px;
            }

            .form-feedback.is-valid {
                display: block;
                color: #10b981;
            }

            .form-feedback.is-invalid {
                display: block;
                color: #ef4444;
            }

            .form-feedback i {
                margin-right: 6px;
            }

            .validation-icon {
                position: absolute;
                right: 16px;
                top: 50%;
                transform: translateY(-50%);
                font-size: 1.2rem;
                opacity: 0;
                transition: all 0.3s ease;
            }

            .form-control-enhanced.is-valid ~ .validation-icon.icon-success {
                opacity: 1;
                color: #10b981;
            }

            .form-control-enhanced.is-invalid ~ .validation-icon.icon-error {
                opacity: 1;
                color: #ef4444;
            }

            /* Password strength indicator */
            .password-strength {
                margin-top: 8px;
                padding-left: 48px;
            }

            .strength-meter {
                height: 4px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 2px;
                overflow: hidden;
                margin-bottom: 6px;
            }

            .strength-meter-fill {
                height: 100%;
                transition: all 0.3s ease;
                border-radius: 2px;
            }

            .strength-weak .strength-meter-fill {
                width: 33%;
                background: #ef4444;
            }

            .strength-medium .strength-meter-fill {
                width: 66%;
                background: #fbbf24;
            }

            .strength-strong .strength-meter-fill {
                width: 100%;
                background: #10b981;
            }

            .strength-text {
                font-size: 0.75rem;
                color: rgba(255, 255, 255, 0.6);
            }

            /* Character counter */
            .char-counter {
                position: absolute;
                right: 16px;
                bottom: -24px;
                font-size: 0.75rem;
                color: rgba(255, 255, 255, 0.5);
            }

            .char-counter.limit-warning {
                color: #fbbf24;
            }

            .char-counter.limit-reached {
                color: #ef4444;
            }

            /* Select enhanced */
            .select-enhanced {
                appearance: none;
                background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='rgba(255,255,255,0.5)' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
                background-repeat: no-repeat;
                background-position: right 16px center;
                padding-right: 48px;
            }

            /* Checkbox/Radio enhanced */
            .form-check-enhanced {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px;
                border-radius: 8px;
                transition: all 0.3s ease;
                cursor: pointer;
            }

            .form-check-enhanced:hover {
                background: rgba(255, 255, 255, 0.05);
            }

            .form-check-input-enhanced {
                width: 20px;
                height: 20px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                background: transparent;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .form-check-input-enhanced:checked {
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                border-color: #3b82f6;
            }

            .form-check-label-enhanced {
                color: rgba(255, 255, 255, 0.8);
                cursor: pointer;
                user-select: none;
            }

            /* Real-time suggestions */
            .form-suggestions {
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: rgba(30, 41, 59, 0.95);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                margin-top: 4px;
                max-height: 200px;
                overflow-y: auto;
                z-index: 1000;
                display: none;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            }

            .form-suggestions.active {
                display: block;
            }

            .suggestion-item {
                padding: 12px 16px;
                cursor: pointer;
                transition: background 0.2s ease;
                color: rgba(255, 255, 255, 0.8);
            }

            .suggestion-item:hover,
            .suggestion-item.selected {
                background: rgba(59, 130, 246, 0.2);
            }

            /* Loading state */
            .form-control-enhanced.loading {
                background-image: linear-gradient(
                    90deg,
                    transparent,
                    rgba(59, 130, 246, 0.1),
                    transparent
                );
                background-size: 200% 100%;
                animation: shimmer-input 1.5s infinite;
            }

            @keyframes shimmer-input {
                0% { background-position: -200% 0; }
                100% { background-position: 200% 0; }
            }

            /* Tooltip */
            .form-tooltip {
                position: absolute;
                top: 50%;
                right: -30px;
                transform: translateY(-50%);
                cursor: help;
                color: rgba(255, 255, 255, 0.4);
                font-size: 1rem;
            }

            .form-tooltip:hover::after {
                content: attr(data-tooltip);
                position: absolute;
                left: 30px;
                top: 50%;
                transform: translateY(-50%);
                background: rgba(15, 23, 42, 0.95);
                backdrop-filter: blur(10px);
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 0.85rem;
                white-space: nowrap;
                z-index: 1001;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            }

            /* Mobile responsive */
            @media (max-width: 768px) {
                .form-control-enhanced {
                    padding: 12px 14px 12px 40px;
                }

                .form-tooltip {
                    position: static;
                    display: block;
                    margin-top: 4px;
                }

                .form-tooltip:hover::after {
                    position: static;
                    display: block;
                    transform: none;
                }
            }
        `;
        document.head.appendChild(style);
    }

    createValidators() {
        return {
            required: {
                validate: (value) => value.trim().length > 0,
                message: 'This field is required'
            },
            email: {
                validate: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
                message: 'Please enter a valid email address'
            },
            phone: {
                validate: (value) => /^[\d\s\-\+\(\)]+$/.test(value) && value.replace(/\D/g, '').length >= 10,
                message: 'Please enter a valid phone number'
            },
            url: {
                validate: (value) => {
                    try {
                        new URL(value);
                        return true;
                    } catch {
                        return false;
                    }
                },
                message: 'Please enter a valid URL'
            },
            minLength: (length) => ({
                validate: (value) => value.length >= length,
                message: `Must be at least ${length} characters`
            }),
            maxLength: (length) => ({
                validate: (value) => value.length <= length,
                message: `Must be no more than ${length} characters`
            }),
            pattern: (regex, message) => ({
                validate: (value) => regex.test(value),
                message: message || 'Invalid format'
            }),
            password: {
                validate: (value) => {
                    return value.length >= 8 &&
                           /[A-Z]/.test(value) &&
                           /[a-z]/.test(value) &&
                           /[0-9]/.test(value);
                },
                message: 'Password must be 8+ characters with uppercase, lowercase, and numbers'
            },
            match: (fieldId) => ({
                validate: (value) => {
                    const matchField = document.getElementById(fieldId);
                    return matchField && value === matchField.value;
                },
                message: 'Fields do not match'
            })
        };
    }

    registerForms() {
        // Auto-register forms with data-validate attribute
        const forms = document.querySelectorAll('form[data-validate]');
        forms.forEach(form => this.registerForm(form));
    }

    registerForm(form) {
        if (typeof form === 'string') {
            form = document.querySelector(form);
        }

        if (!form) return;

        const formData = {
            element: form,
            fields: new Map()
        };

        // Register all input fields
        const inputs = form.querySelectorAll('[data-validate-rules]');
        inputs.forEach(input => {
            this.registerField(input, formData);
        });

        // Handle form submission
        form.addEventListener('submit', (e) => {
            if (!this.validateForm(formData)) {
                e.preventDefault();
                e.stopPropagation();
            }
        });

        this.forms.set(form, formData);
    }

    registerField(input, formData) {
        const rules = JSON.parse(input.dataset.validateRules || '[]');
        
        const fieldData = {
            element: input,
            rules,
            isValid: false
        };

        formData.fields.set(input, fieldData);

        // Add event listeners
        if (this.options.validateOnInput) {
            input.addEventListener('input', () => this.validateField(fieldData));
        }

        if (this.options.validateOnBlur) {
            input.addEventListener('blur', () => this.validateField(fieldData));
        }

        // Password strength meter
        if (input.type === 'password' && input.dataset.strengthMeter) {
            this.addPasswordStrengthMeter(input);
        }

        // Character counter
        if (input.dataset.charCounter) {
            this.addCharCounter(input);
        }
    }

    validateField(fieldData) {
        const input = fieldData.element;
        const value = input.value;
        let isValid = true;
        let errorMessage = '';

        // Check each rule
        for (const rule of fieldData.rules) {
            const validator = this.getValidator(rule);
            
            if (!validator) continue;

            if (!validator.validate(value)) {
                isValid = false;
                errorMessage = validator.message;
                break;
            }
        }

        // Update UI
        this.updateFieldUI(input, isValid, errorMessage);
        fieldData.isValid = isValid;

        return isValid;
    }

    getValidator(rule) {
        if (typeof rule === 'string') {
            return this.validators[rule];
        } else if (typeof rule === 'object' && rule.type) {
            if (typeof this.validators[rule.type] === 'function') {
                return this.validators[rule.type](rule.value);
            }
            return this.validators[rule.type];
        }
        return null;
    }

    updateFieldUI(input, isValid, errorMessage) {
        input.classList.remove('is-valid', 'is-invalid');
        
        if (input.value.length > 0) {
            input.classList.add(isValid ? 'is-valid' : 'is-invalid');
        }

        // Update feedback message
        let feedback = input.parentElement.querySelector('.form-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'form-feedback';
            input.parentElement.appendChild(feedback);
        }

        feedback.classList.remove('is-valid', 'is-invalid');
        
        if (input.value.length > 0) {
            if (isValid) {
                feedback.classList.add('is-valid');
                feedback.innerHTML = '<i class="bi bi-check-circle-fill"></i>Looks good!';
            } else {
                feedback.classList.add('is-invalid');
                feedback.innerHTML = `<i class="bi bi-exclamation-circle-fill"></i>${errorMessage}`;
            }
        }
    }

    validateForm(formData) {
        let allValid = true;
        let firstInvalidField = null;

        // Validate all fields
        formData.fields.forEach((fieldData) => {
            const isValid = this.validateField(fieldData);
            if (!isValid) {
                allValid = false;
                if (!firstInvalidField) {
                    firstInvalidField = fieldData.element;
                }
            }
        });

        // Scroll to first error
        if (!allValid && firstInvalidField && this.options.scrollToError) {
            firstInvalidField.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
            firstInvalidField.focus();
        }

        return allValid;
    }

    addPasswordStrengthMeter(input) {
        const container = document.createElement('div');
        container.className = 'password-strength';
        container.innerHTML = `
            <div class="strength-meter">
                <div class="strength-meter-fill"></div>
            </div>
            <div class="strength-text">Password strength: <span></span></div>
        `;
        
        input.parentElement.appendChild(container);

        input.addEventListener('input', () => {
            const strength = this.calculatePasswordStrength(input.value);
            const meter = container.querySelector('.strength-meter');
            const text = container.querySelector('.strength-text span');

            meter.className = 'strength-meter strength-' + strength.level;
            text.textContent = strength.label;
        });
    }

    calculatePasswordStrength(password) {
        let score = 0;

        if (password.length >= 8) score++;
        if (password.length >= 12) score++;
        if (/[a-z]/.test(password)) score++;
        if (/[A-Z]/.test(password)) score++;
        if (/[0-9]/.test(password)) score++;
        if (/[^a-zA-Z0-9]/.test(password)) score++;

        if (score <= 2) return { level: 'weak', label: 'Weak' };
        if (score <= 4) return { level: 'medium', label: 'Medium' };
        return { level: 'strong', label: 'Strong' };
    }

    addCharCounter(input) {
        const maxLength = parseInt(input.dataset.charCounter);
        const counter = document.createElement('div');
        counter.className = 'char-counter';
        input.parentElement.style.position = 'relative';
        input.parentElement.appendChild(counter);

        const updateCounter = () => {
            const current = input.value.length;
            counter.textContent = `${current}/${maxLength}`;
            
            counter.classList.remove('limit-warning', 'limit-reached');
            if (current >= maxLength) {
                counter.classList.add('limit-reached');
            } else if (current >= maxLength * 0.9) {
                counter.classList.add('limit-warning');
            }
        };

        input.addEventListener('input', updateCounter);
        updateCounter();
    }
}

// Global instance
window.enhancedFormValidation = new EnhancedFormValidation();

// Auto-initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    window.enhancedFormValidation.registerForms();
});
