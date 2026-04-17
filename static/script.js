const API_BASE = "http://127.0.0.1:5000";

/**
 * HELPER: Get the JWT token from localStorage
 */
const getAuthHeader = () => {
    const token = localStorage.getItem('token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
};

// --- 👤 AUTHENTICATION ---
async function handleLogin(e) {
    e.preventDefault();
    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;

    // 1. Ensure the URL is /auth/login
    const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: user, password: pass })
    });

    const data = await response.json();
    if (response.ok) {
        // 2. Use access_token (matching your Python code)
        localStorage.setItem('token', data.access_token); 
        localStorage.setItem('username', data.username);
        localStorage.setItem('role', data.role);
        window.location.href = 'dashboard.html';
    } else {
        const errorDiv = document.getElementById('error-msg');
        errorDiv.innerText = data.msg || "Invalid credentials";
        errorDiv.style.display = 'block';
    }
}

// --- 📁 FILE UPLOAD (with JWT) ---
function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const status = document.getElementById('upload-status');
    const progBar = document.getElementById('progress-bar');

    if (!fileInput.files[0]) return alert("Select a file first");

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const xhr = new XMLHttpRequest();
    // Path updated to match file_bp (URL prefix: /files)
    xhr.open("POST", `${API_BASE}/files/upload`, true);
    
    // IMPORTANT: Include the JWT Token
    xhr.setRequestHeader("Authorization", `Bearer ${localStorage.getItem('token')}`);

    document.querySelector('.progress-container').style.display = 'block';

    xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
            progBar.style.width = (e.loaded / e.total * 100) + "%";
        }
    };

    xhr.onload = () => {
        status.style.display = 'block';
        const res = JSON.parse(xhr.responseText);
        if (xhr.status === 200) {
            status.className = "alert success";
            status.innerText = "File Encrypted & Stored Successfully!";
            fileInput.value = "";
        } else {
            status.className = "alert error";
            status.innerText = res.msg || "Upload failed.";
        }
    };
    xhr.send(formData);
}

// --- 📊 DATA LOADING (with JWT) ---
async function loadFiles() {
    const tableBody = document.getElementById('file-table');
    if (!tableBody) return;

    try {
        const res = await fetch(`${API_BASE}/files/list`, {
            headers: getAuthHeader()
        });
        
        if (res.status === 401) return logout(); // Token expired

        const files = await res.json();
        tableBody.innerHTML = files.map(f => `
            <tr>
                <td>${f.filename}</td>
                <td>${new Date(f.date).toLocaleString()}</td>
                <td><span class="badge">${f.owner}</span></td>
                <td><button class="btn-sm" onclick='downloadFile(${JSON.stringify(encodeURIComponent(f.filename))})'>Download</button></td>
            </tr>
        `).join('');
    } catch (err) {
        console.error("Error loading files:", err);
    }
}

async function downloadFile(encodedFilename) {
    try {
        const response = await fetch(`${API_BASE}/files/download/${encodedFilename}`, {
            headers: getAuthHeader()
        });

        if (response.status === 401) return logout();

        if (!response.ok) {
            const error = await response.json().catch(() => ({ msg: "Download failed." }));
            alert(error.msg || "Download failed.");
            return;
        }

        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        const decodedFilename = decodeURIComponent(encodedFilename);

        link.href = downloadUrl;
        link.download = decodedFilename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(downloadUrl);
    } catch (err) {
        console.error("Error downloading file:", err);
        alert("Unable to download file right now.");
    }
}

async function loadLogs() {
    const tableBody = document.getElementById('logs-table');
    if (!tableBody) return;

    try {
        // Path updated to /logs/all (Admin only)
        const res = await fetch(`${API_BASE}/logs/all`, {
            headers: getAuthHeader()
        });

        if (res.status === 403) {
            tableBody.innerHTML = "<tr><td colspan='4'>Access Denied: Admin Only</td></tr>";
            return;
        }

        const logs = await res.json();
        tableBody.innerHTML = logs.map(l => `
            <tr>
                <td>${l.user_id}</td>
                <td>${l.action}</td>
                <td>${new Date(l.timestamp).toLocaleString()}</td>
                <td><span style="color: ${l.status === 'SUCCESS' ? 'var(--accent)' : 'var(--error)'}">${l.status}</span></td>
            </tr>
        `).join('');
    } catch (err) {
        console.error("Error loading logs:", err);
    }
}

// --- 🚨 ATTACK SIMULATION ---
function simulateAttack(type) {
    const consoleBox = document.getElementById('console');
    const logLine = (msg) => {
        const div = document.createElement('div');
        div.innerText = `> [${new Date().toLocaleTimeString()}] ${msg}`;
        consoleBox.appendChild(div);
        consoleBox.scrollTop = consoleBox.scrollHeight;
    };

    logLine(`Starting ${type} Simulation...`);
    
    // Call the backend to record the "attack" in the security logs
    fetch(`${API_BASE}/attacks/simulate`, {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            ...getAuthHeader() 
        },
        body: JSON.stringify({ attack_type: type })
    })
    .then(res => res.json())
    .then(data => {
        setTimeout(() => logLine(`Result: ${data.result}`), 1000);
        setTimeout(() => logLine(`System Status: Logged and Blocked.`), 1800);
    });
}

// --- ⚙️ AUTO-LOAD ON PAGE ARRIVAL ---
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    
    // Redirect to login if no token found
    if (!token && !window.location.pathname.includes('login.html')) {
        window.location.href = 'login.html';
    }

    // Load data based on page
    if (window.location.pathname.includes('files.html')) loadFiles();
    if (window.location.pathname.includes('logs.html')) loadLogs();
    
    // Display Username
    const userDisplay = document.getElementById('user-welcome');
    if (userDisplay) {
        userDisplay.innerText = `Welcome, ${localStorage.getItem('username')} [${localStorage.getItem('role')}]`;
    }

    // Admin-only Link Logic
    const logNav = document.getElementById('nav-logs');
    if (logNav && localStorage.getItem('role') !== 'admin') {
        logNav.style.display = 'none';
    }
});

function logout() {
    localStorage.clear();
    window.location.href = 'login.html';
}
