const updateExpenseInputState = (checkbox, input) => {
    input.disabled = !checkbox.checked;
    input.required = checkbox.checked;
    if (!checkbox.checked) input.value = '';
    updateTotals();
};

const updateTotals = () => {
    const incomeInput = document.getElementById('income');
    const income = parseFloat(incomeInput.value) || 0;
    let total = 0;

    document.querySelectorAll('.form-check-input').forEach(checkbox => {
        const input = checkbox.closest('.row').querySelector('input[type="number"]');
        if (checkbox.checked && input && input.value) {
            total += parseFloat(input.value) || 0;
        }
    });

    const net = income - total;
    const totalField = document.getElementById('total_expenses');
    const netField = document.getElementById('net_savings');
    const warning = document.getElementById('warningMessage');
    const submitBtn = document.querySelector('button[type="submit"]');

    totalField.value = total.toFixed(2);
    netField.value = net.toFixed(2);

    const overBudget = total > income;

    totalField.classList.toggle('border-danger', overBudget);
    netField.classList.toggle('border-danger', overBudget);
    warning.style.display = overBudget ? 'block' : 'none';
    submitBtn.disabled = overBudget;
};

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.form-check-input').forEach(checkbox => {
        const input = checkbox.closest('.row').querySelector('input[type="number"]');
        updateExpenseInputState(checkbox, input);
        checkbox.addEventListener('change', () => updateExpenseInputState(checkbox, input));
        input.addEventListener('input', updateTotals);
    });

    document.getElementById('income').addEventListener('input', updateTotals);

    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('input', () => {
            if (input.value < 0) input.value = '';
        });
    });

    // Bootstrap validation
    (() => {
        'use strict';
        const forms = document.querySelectorAll('.needs-validation');
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    })();
});
