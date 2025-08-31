// ===============================
// Skill Exchange Network - Upgraded JS
// ===============================
document.addEventListener('DOMContentLoaded', function () {
    SkillExchangeApp.init();
});

const SkillExchangeApp = {
    init() {
        this.initializeFormValidation();
        this.initializeSkillSelection();
        this.initializeSessionScheduling();
        this.initializeSearchFunctionality();
        this.initializeFormLoadingState();
        this.addSkillCardAnimations();
        this.handleNetworkStatus();
        this.addRealTimeValidation();
        this.restoreFormData();
    },

    // ---------------- Form Validation ----------------
    initializeFormValidation() {
        const registrationForm = document.getElementById('registrationForm');
        if (registrationForm) {
            registrationForm.addEventListener('submit', (e) => {
                if (!this.validateRegistrationForm()) {
                    e.preventDefault();
                    this.showAlert('⚠️ Please fill in all required fields and select at least one skill.', 'warning');
                } else {
                    this.saveFormData();
                }
            });
        }
    },

    validateRegistrationForm() {
        const name = document.getElementById('name')?.value.trim();
        const email = document.getElementById('email')?.value.trim();
        const division = document.getElementById('division')?.value.trim();

        if (!name || !email || !division) return false;

        const teachSkills = document.querySelectorAll('input[name="teach_skills"]:checked');
        const learnSkills = document.querySelectorAll('input[name="learn_skills"]:checked');
        if (teachSkills.length === 0 && learnSkills.length === 0) return false;

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            this.showAlert('❌ Please enter a valid email address.', 'danger');
            return false;
        }

        return true;
    },

    // ---------------- Skill Selection ----------------
    initializeSkillSelection() {
        document.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
            checkbox.addEventListener('change', () => this.updateSkillSelection());
        });
    },

    updateSkillSelection() {
        document.querySelectorAll('input[name="teach_skills"]:checked, input[name="learn_skills"]:checked')
            .forEach(skill => skill.parentElement.classList.add('selected-skill'));

        document.querySelectorAll('input[type="checkbox"]:not(:checked)')
            .forEach(skill => skill.parentElement.classList.remove('selected-skill'));
    },

    // ---------------- Session Scheduling ----------------
    initializeSessionScheduling() {
        const scheduleBtns = document.querySelectorAll('.schedule-btn');
        scheduleBtns.forEach(btn => {
            btn.addEventListener('click', () => this.scheduleSession());
        });
    },

    scheduleSession() {
        // Mock modal for now
        this.showAlert('📅 Contact your partner via email to schedule your session!', 'info');
    },

    // ---------------- Search Functionality ----------------
    initializeSearchFunctionality() {
        const searchInput = document.querySelector('input[name="search"]');
        const skillCards = document.querySelectorAll('.skill-card');

        if (searchInput) {
            searchInput.addEventListener('input', function () {
                const query = this.value.toLowerCase();
                skillCards.forEach(card => {
                    card.style.display = card.textContent.toLowerCase().includes(query) ? '' : 'none';
                });
            });
        }
    },

    // ---------------- Loading State ----------------
    initializeFormLoadingState() {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function () {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                    submitBtn.disabled = true;
                }
            });
        });
    },

    // ---------------- Utility: Alerts ----------------
    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show mt-2`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
            setTimeout(() => alertDiv.remove(), 5000);
        }
    },

    // ---------------- Animations ----------------
    addSkillCardAnimations() {
        document.querySelectorAll('.skill-card').forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
            card.classList.add('animate-fade-in');
        });
    },

    // ---------------- Network Status ----------------
    handleNetworkStatus() {
        window.addEventListener('online', () => this.showAlert('✅ Connection restored!', 'success'));
        window.addEventListener('offline', () => this.showAlert('⚠️ Connection lost. Some features may not work properly.', 'warning'));
    },

    // ---------------- Real-Time Validation ----------------
    addRealTimeValidation() {
        const emailInput = document.getElementById('email');
        if (emailInput) {
            emailInput.addEventListener('blur', () => {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (emailInput.value && !emailRegex.test(emailInput.value)) {
                    emailInput.classList.add('is-invalid');
                    this.showValidationMessage(emailInput, '❌ Please enter a valid email address.');
                } else {
                    emailInput.classList.remove('is-invalid');
                    emailInput.classList.add('is-valid');
                }
            });
        }
    },

    showValidationMessage(input, message) {
        const existingFeedback = input.nextElementSibling;
        if (existingFeedback && existingFeedback.classList.contains('invalid-feedback')) {
            existingFeedback.remove();
        }
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        feedback.textContent = message;
        input.parentNode.insertBefore(feedback, input.nextSibling);
    },

    // ---------------- Form Persistence ----------------
    saveFormData() {
        const formData = {
            name: document.getElementById('name')?.value,
            email: document.getElementById('email')?.value,
            division: document.getElementById('division')?.value
        };
        localStorage.setItem('registrationForm', JSON.stringify(formData));
    },

    restoreFormData() {
        const savedData = localStorage.getItem('registrationForm');
        if (savedData) {
            const { name, email, division } = JSON.parse(savedData);
            if (name) document.getElementById('name').value = name;
            if (email) document.getElementById('email').value = email;
            if (division) document.getElementById('division').value = division;
        }
    }
};

// ---------------- Extra CSS (Injected) ----------------
const style = document.createElement('style');
style.textContent = `
    .selected-skill { background-color: #e3f2fd !important; border-radius: 5px; font-weight: bold; }
    .animate-fade-in { animation: fadeInUp 0.6s ease-out forwards; }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
    .is-invalid { border-color: #dc3545; }
    .is-valid { border-color: #28a745; }
`;
document.head.appendChild(style);
