// AI Study Buddy Frontend JavaScript

const API_BASE = window.location.origin;

// State Management
let uploadedFiles = [];
let materials = [];
let currentQuestion = '';
let currentExplanation = '';
let subjects = ['Mathematics', 'Biology'];

// Materials (including extracted text) are kept client-side rather than
// fetched from the server: on a serverless deployment, each request can
// hit a different backend instance with no memory of previous uploads.
const MATERIALS_STORAGE_KEY = 'finalsArcMaterials';

function loadMaterialsFromStorage() {
    try {
        const stored = localStorage.getItem(MATERIALS_STORAGE_KEY);
        materials = stored ? JSON.parse(stored) : [];
    } catch (error) {
        console.error('Error reading materials from storage:', error);
        materials = [];
    }
    displayMaterials();
    updateMaterialSelects();
}

function saveMaterialsToStorage() {
    try {
        localStorage.setItem(MATERIALS_STORAGE_KEY, JSON.stringify(materials));
    } catch (error) {
        console.error('Error saving materials to storage:', error);
    }
}

function getMaterialContent(materialId) {
    const material = materials.find(m => m.material_id === materialId);
    return material ? material.full_text : undefined;
}

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const materialsList = document.getElementById('materialsList');
const loadingOverlay = document.getElementById('loadingOverlay');
const addSubjectBtn = document.getElementById('addSubjectBtn');
const subjectInput = document.getElementById('subjectInput');
const subjectTags = document.getElementById('subjectTags');

// Initialize subjects display
window.addEventListener('DOMContentLoaded', () => {
    renderSubjectTags();
});

// Subject Tag Management
// Make removeSubject globally accessible
window.removeSubject = function(subject) {
    subjects = subjects.filter(s => s !== subject);
    renderSubjectTags();
};
addSubjectBtn.addEventListener('click', () => {
    subjectInput.style.display = 'block';
    subjectInput.focus();
    addSubjectBtn.style.display = 'none';
});

subjectInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && subjectInput.value.trim()) {
        addSubject(subjectInput.value.trim());
        subjectInput.value = '';
        subjectInput.style.display = 'none';
        addSubjectBtn.style.display = 'block';
    } else if (e.key === 'Escape') {
        subjectInput.value = '';
        subjectInput.style.display = 'none';
        addSubjectBtn.style.display = 'block';
    }
});

subjectInput.addEventListener('blur', () => {
    setTimeout(() => {
        if (subjectInput.value.trim()) {
            addSubject(subjectInput.value.trim());
        }
        subjectInput.value = '';
        subjectInput.style.display = 'none';
        addSubjectBtn.style.display = 'block';
    }, 200);
});

function addSubject(subject) {
    if (!subjects.includes(subject)) {
        subjects.push(subject);
        renderSubjectTags();
    }
}

function renderSubjectTags() {
    subjectTags.innerHTML = subjects.map(subject => `
        <div class="subject-tag">
            ${subject}
            <button class="remove-subject" onclick="removeSubject('${subject}')">×</button>
        </div>
    `).join('');
}

// Tab Management
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;
        switchTab(tabName);
    });
});

function switchTab(tabName) {
    // Update buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');
}

// Upload Functionality
uploadArea.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#666';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = '';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '';
    fileInput.files = e.dataTransfer.files;
    updateFileDisplay();
});

fileInput.addEventListener('change', updateFileDisplay);

function updateFileDisplay() {
    uploadedFiles = Array.from(fileInput.files);
    if (uploadedFiles.length > 0) {
        const fileNames = uploadedFiles.map(f => f.name).join(', ');
        uploadArea.querySelector('.upload-text').textContent = `Selected: ${fileNames}`;
    }
}

uploadBtn.addEventListener('click', uploadFiles);

async function uploadFiles() {
    if (uploadedFiles.length === 0) {
        alert('Please select files to upload');
        return;
    }

    showLoading(true);

    try {
        for (const file of uploadedFiles) {
            const formData = new FormData();
            formData.append('file', file);
            if (subjects.length > 0) {
                formData.append('subject', subjects.join(', '));
            }

            const response = await fetch(`${API_BASE}/api/upload`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (!result.success) {
                throw new Error(result.detail || 'Upload failed');
            }

            materials.push({
                material_id: result.material_id,
                file_name: result.filename,
                format: result.format,
                content_length: (result.full_text || '').length,
                full_text: result.full_text || ''
            });
            saveMaterialsToStorage();

            showNotification(`✅ ${file.name} uploaded successfully!`, 'success');
        }

        // Reset
        fileInput.value = '';
        uploadedFiles = [];
        uploadArea.querySelector('.upload-text').textContent = 'Drop files or ';
        uploadArea.querySelector('.upload-text').innerHTML = 'Drop files or <span class="browse-link">browse</span>';
        subjects = [];
        renderSubjectTags();

        displayMaterials();
        updateMaterialSelects();

    } catch (error) {
        showNotification(`❌ Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

function displayMaterials() {
    if (materials.length === 0) {
        materialsList.innerHTML = '<p class="empty-state">No materials uploaded yet</p>';
        return;
    }

    materialsList.innerHTML = materials.map(mat => `
        <div class="material-card">
            <div class="material-info">
                <h4>📄 ${mat.file_name || 'Unknown file'}</h4>
                <p>Format: ${mat.format} | Size: ${formatBytes(mat.content_length)}</p>
            </div>
            <button class="btn btn-danger" onclick="deleteMaterial('${mat.material_id}')">Delete</button>
        </div>
    `).join('');
}

function updateMaterialSelects() {
    const selects = ['notesMaterial', 'askMaterial', 'quizMaterial'];
    
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        const firstOption = select.querySelector('option:first-child');
        
        select.innerHTML = firstOption.outerHTML + materials.map(mat => `
            <option value="${mat.material_id}">${mat.file_name || 'Unknown'}</option>
        `).join('');
    });
}

async function deleteMaterial(materialId) {
    if (!confirm('Are you sure you want to delete this material?')) return;

    materials = materials.filter(m => m.material_id !== materialId);
    saveMaterialsToStorage();
    displayMaterials();
    updateMaterialSelects();
    showNotification('Material deleted', 'success');

    // Best-effort server-side cleanup; ignore failures since the backend
    // may not have this material in memory (serverless instance mismatch)
    try {
        await fetch(`${API_BASE}/api/material/${materialId}`, { method: 'DELETE' });
    } catch (error) {
        console.error('Error cleaning up material on server:', error);
    }
}

// Generate Notes
document.getElementById('generateNotesBtn').addEventListener('click', generateNotes);

async function generateNotes() {
    const materialId = document.getElementById('notesMaterial').value;
    const level = document.getElementById('notesLevel').value;
    const focus = document.getElementById('notesFocus').value;

    if (!materialId) {
        alert('Please select a material');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE}/api/generate-notes`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                material_id: materialId,
                level,
                focus,
                material_content: getMaterialContent(materialId)
            })
        });

        const result = await response.json();

        if (result.success) {
            displayNotes(result.notes);
            showNotification('Notes generated successfully!', 'success');
        } else {
            throw new Error(result.error || 'Failed to generate notes');
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

function displayNotes(notes) {
    console.log('Displaying notes:', notes.substring(0, 100));
    const output = document.getElementById('notesOutput');
    if (!output) {
        console.error('notesOutput element not found!');
        return;
    }
    // Use simple conversion since marked might not be loaded
    output.innerHTML = convertMarkdown(notes);
    output.style.display = 'block';
    output.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Ask Questions
document.getElementById('askBtn').addEventListener('click', askQuestion);

async function askQuestion() {
    const question = document.getElementById('questionInput').value.trim();
    const materialId = document.getElementById('askMaterial').value;
    const level = document.getElementById('askLevel').value;

    if (!question) {
        alert('Please enter a question');
        return;
    }

    currentQuestion = question;
    showLoading(true);

    try {
        const response = await fetch(`${API_BASE}/api/ask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question,
                material_id: materialId || null,
                level,
                material_content: materialId ? getMaterialContent(materialId) : undefined
            })
        });

        const result = await response.json();

        if (result.success) {
            currentExplanation = result.explanation;
            displayAnswer(result.explanation);
            document.getElementById('simplerExplanation').style.display = 'block';
            showNotification('Question answered!', 'success');
        } else {
            throw new Error(result.error || 'Failed to answer question');
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

function displayAnswer(answer) {
    console.log('Displaying answer:', answer.substring(0, 100));
    const output = document.getElementById('answerOutput');
    if (!output) {
        console.error('answerOutput element not found!');
        return;
    }
    output.innerHTML = convertMarkdown(answer);
    output.style.display = 'block';
    output.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Simpler Explanation
document.getElementById('simplerBtn').addEventListener('click', getSimplerExplanation);

async function getSimplerExplanation() {
    if (!currentQuestion || !currentExplanation) return;

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE}/api/explain-simpler`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                original_explanation: currentExplanation,
                question: currentQuestion
            })
        });

        const result = await response.json();

        if (result.success) {
            currentExplanation = result.explanation;
            displayAnswer(result.explanation);
            showNotification('Simpler explanation provided!', 'success');
        } else {
            throw new Error(result.error || 'Failed to simplify');
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Generate Quiz
document.getElementById('generateQuizBtn').addEventListener('click', generateQuiz);

async function generateQuiz() {
    const materialId = document.getElementById('quizMaterial').value;
    const numQuestions = parseInt(document.getElementById('numQuestions').value);
    const difficulty = document.getElementById('quizDifficulty').value;

    if (!materialId) {
        alert('Please select a material');
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE}/api/generate-quiz`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                material_id: materialId,
                num_questions: numQuestions,
                difficulty,
                material_content: getMaterialContent(materialId)
            })
        });

        const result = await response.json();

        if (result.success) {
            displayQuiz(result.questions);
            showNotification('Quiz generated!', 'success');
        } else {
            throw new Error(result.error || 'Failed to generate quiz');
        }
    } catch (error) {
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

function displayQuiz(questions) {
    const output = document.getElementById('quizOutput');
    
    output.innerHTML = questions.map((q, index) => `
        <div class="question-card">
            <div class="question-header">
                <span class="question-number">Question ${q.id || index + 1}</span>
                <span class="difficulty-badge difficulty-${q.difficulty}">${q.difficulty.toUpperCase()}</span>
            </div>
            <div class="question-text">${q.question}</div>
            
            ${q.options ? `
                <ul class="options-list">
                    ${q.options.map(opt => `<li class="option-item">${opt}</li>`).join('')}
                </ul>
            ` : ''}
            
            <button class="show-solution-btn" onclick="toggleSolution(${index})">
                Show Solution
            </button>
            
            <div id="solution-${index}" class="solution" style="display: none;">
                <h4>✅ Correct Answer: ${q.correct_answer}</h4>
                <p><strong>💡 Explanation:</strong></p>
                <p>${q.explanation ? q.explanation.replace(/\n/g, '<br>') : 'No explanation provided'}</p>
                
                ${q.hints ? `
                    <p><strong>🔍 Hints:</strong></p>
                    <ul>
                        ${q.hints.map(hint => `<li>${hint}</li>`).join('')}
                    </ul>
                ` : ''}
                
                ${q.key_concept ? `
                    <p><strong>🎯 Key Concept:</strong> ${q.key_concept}</p>
                ` : ''}
            </div>
        </div>
    `).join('');
}

function toggleSolution(index) {
    const solution = document.getElementById(`solution-${index}`);
    solution.style.display = solution.style.display === 'none' ? 'block' : 'none';
}

// Utilities
function showLoading(show) {
    loadingOverlay.classList.toggle('active', show);
}

function showNotification(message, type = 'info') {
    // Simple alert for now - can be enhanced with toast notifications
    console.log(`[${type.toUpperCase()}] ${message}`);
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function convertMarkdown(text) {
    if (!text) return '';
    
    // Escape HTML first
    let html = text;
    
    // Convert code blocks
    html = html.replace(/```(.*?)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>');
    
    // Convert inline code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Convert headers
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    
    // Convert bold and italic
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Convert lists
    html = html.replace(/^\- (.*$)/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    
    // Convert line breaks and paragraphs
    html = html.replace(/\n\n/g, '</p><p>');
    html = html.replace(/\n/g, '<br>');
    
    // Wrap in paragraphs
    html = '<p>' + html + '</p>';
    
    // Clean up
    html = html.replace(/<p><\/p>/g, '');
    html = html.replace(/<p>(<h[1-6]>)/g, '$1');
    html = html.replace(/(<\/h[1-6]>)<\/p>/g, '$1');
    html = html.replace(/<p>(<ul>)/g, '$1');
    html = html.replace(/(<\/ul>)<\/p>/g, '$1');
    html = html.replace(/<p>(<pre>)/g, '$1');
    html = html.replace(/(<\/pre>)<\/p>/g, '$1');
    
    return html;
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadMaterialsFromStorage();
});
