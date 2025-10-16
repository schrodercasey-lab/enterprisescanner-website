/**
 * Enterprise User Management JavaScript
 * Manages user accounts, roles, permissions, and SSO configuration
 */

class UserManagementSystem {
    constructor() {
        this.apiBase = '/api';
        this.currentOrgId = 'org-1'; // Would be dynamically set based on current user
        this.currentData = {
            users: [],
            roles: {},
            permissions: {},
            auditLogs: [],
            organizations: []
        };
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadInitialData();
        this.updateSummaryCards();
    }

    setupEventListeners() {
        // Main action buttons
        document.getElementById('refreshUsers').addEventListener('click', () => {
            this.loadUserData();
        });

        document.getElementById('addUserBtn').addEventListener('click', () => {
            this.showAddUserModal();
        });

        document.getElementById('createOrgBtn').addEventListener('click', () => {
            this.showCreateOrgModal();
        });

        // Modal save buttons
        document.getElementById('saveUserBtn').addEventListener('click', () => {
            this.saveUser();
        });

        document.getElementById('saveOrgBtn').addEventListener('click', () => {
            this.saveOrganization();
        });

        // Form toggles
        document.getElementById('isSSOUser').addEventListener('change', (e) => {
            this.togglePasswordSection(!e.target.checked);
        });

        // Search and filters
        document.getElementById('userSearch').addEventListener('input', () => {
            this.filterUsers();
        });

        document.getElementById('roleFilter').addEventListener('change', () => {
            this.filterUsers();
        });

        document.getElementById('auditActionFilter').addEventListener('change', () => {
            this.filterAuditLogs();
        });

        // Tab changes
        document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                const targetTab = e.target.getAttribute('data-bs-target');
                this.handleTabChange(targetTab);
            });
        });

        // Export functionality
        document.getElementById('exportAuditLogs').addEventListener('click', () => {
            this.exportAuditLogs();
        });

        // Logout functionality
        document.getElementById('logoutBtn').addEventListener('click', () => {
            this.logout();
        });
    }

    async loadInitialData() {
        try {
            this.showStatus('Loading user management data...', 'info');
            
            // Load roles and permissions first
            await Promise.all([
                this.loadRoles(),
                this.loadPermissions()
            ]);
            
            // Then load users and other data
            await Promise.all([
                this.loadUserData(),
                this.loadAuditLogs()
            ]);
            
            this.hideStatus();
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showStatus('Failed to load user management data', 'error');
        }
    }

    async loadUserData() {
        try {
            const response = await fetch(`${this.apiBase}/organizations/${this.currentOrgId}/users`);
            const result = await response.json();

            if (result.status === 'success') {
                this.currentData.users = result.data.users;
                this.displayUsers();
                this.updateSummaryCards();
            } else {
                throw new Error(result.message || 'Failed to load users');
            }
        } catch (error) {
            console.error('Error loading users:', error);
            this.showStatus('Failed to load user data', 'error');
        }
    }

    async loadRoles() {
        try {
            const response = await fetch(`${this.apiBase}/roles`);
            const result = await response.json();

            if (result.status === 'success') {
                this.currentData.roles = result.data.roles;
                this.populateRoleSelectors();
                this.displayRolesMatrix();
            }
        } catch (error) {
            console.error('Error loading roles:', error);
        }
    }

    async loadPermissions() {
        try {
            const response = await fetch(`${this.apiBase}/permissions`);
            const result = await response.json();

            if (result.status === 'success') {
                this.currentData.permissions = result.data.permissions;
            }
        } catch (error) {
            console.error('Error loading permissions:', error);
        }
    }

    async loadAuditLogs() {
        try {
            const response = await fetch(`${this.apiBase}/organizations/${this.currentOrgId}/audit-logs?limit=100`);
            const result = await response.json();

            if (result.status === 'success') {
                this.currentData.auditLogs = result.data.audit_logs;
                this.displayAuditLogs();
            }
        } catch (error) {
            console.error('Error loading audit logs:', error);
        }
    }

    updateSummaryCards() {
        const users = this.currentData.users;
        
        // Total users
        document.getElementById('totalUsers').textContent = users.length;
        
        // Active sessions (mock data)
        const activeSessions = users.filter(u => u.last_login && 
            new Date(u.last_login) > new Date(Date.now() - 24 * 60 * 60 * 1000)).length;
        document.getElementById('activeSessions').textContent = activeSessions;
        
        // SSO users
        const ssoUsers = users.filter(u => u.is_sso_user).length;
        document.getElementById('ssoUsers').textContent = ssoUsers;
        
        // Organizations (mock)
        document.getElementById('totalOrgs').textContent = '1';
        
        // Animate counters
        this.animateCounters();
    }

    animateCounters() {
        const counters = document.querySelectorAll('.card-title');
        counters.forEach(counter => {
            const target = parseInt(counter.textContent);
            if (isNaN(target)) return;

            let current = 0;
            const increment = target / 30;
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    counter.textContent = target;
                    clearInterval(timer);
                } else {
                    counter.textContent = Math.floor(current);
                }
            }, 50);
        });
    }

    displayUsers() {
        const container = document.getElementById('usersTable');
        if (!this.currentData.users || this.currentData.users.length === 0) {
            container.innerHTML = '<p class="text-muted text-center py-4">No users found</p>';
            return;
        }

        const html = `
            <div class="table-responsive">
                <table class="table user-table">
                    <thead>
                        <tr>
                            <th>User</th>
                            <th>Role</th>
                            <th>Status</th>
                            <th>Last Login</th>
                            <th>SSO</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.currentData.users.map(user => this.generateUserRow(user)).join('')}
                    </tbody>
                </table>
            </div>
        `;

        container.innerHTML = html;
    }

    generateUserRow(user) {
        const statusClass = user.is_active ? 'status-active' : 'status-inactive';
        const statusText = user.is_active ? 'Active' : 'Inactive';
        const lastLogin = user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never';
        const ssoIcon = user.is_sso_user ? 
            '<i class="bi bi-check-circle-fill text-success"></i>' : 
            '<i class="bi bi-x-circle-fill text-muted"></i>';

        return `
            <tr>
                <td>
                    <div class="d-flex align-items-center">
                        <div class="user-avatar me-3">
                            ${user.first_name.charAt(0)}${user.last_name.charAt(0)}
                        </div>
                        <div>
                            <div class="fw-bold">${user.first_name} ${user.last_name}</div>
                            <div class="text-muted small">${user.email}</div>
                        </div>
                    </div>
                </td>
                <td>
                    <span class="role-badge role-${user.role.replace('_', '-')}">${this.formatRoleName(user.role)}</span>
                </td>
                <td>
                    <span class="status-indicator ${statusClass}"></span>
                    ${statusText}
                </td>
                <td>${lastLogin}</td>
                <td>${ssoIcon}</td>
                <td>
                    <button class="action-btn action-btn-view" onclick="userMgmt.viewUser('${user.user_id}')" title="View Details">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="action-btn action-btn-edit" onclick="userMgmt.editUser('${user.user_id}')" title="Edit User">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="action-btn action-btn-delete" onclick="userMgmt.deleteUser('${user.user_id}')" title="Delete User">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }

    displayRolesMatrix() {
        const container = document.getElementById('rolesMatrix');
        const roles = this.currentData.roles;
        const permissions = this.currentData.permissions;

        if (!roles || !permissions) {
            container.innerHTML = '<p class="text-muted text-center py-4">Loading roles and permissions...</p>';
            return;
        }

        const permissionKeys = Object.keys(permissions);
        const roleKeys = Object.keys(roles);

        const html = `
            <div class="permission-matrix">
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>Permission</th>
                            ${roleKeys.map(role => `<th class="text-center">${this.formatRoleName(role)}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${permissionKeys.map(permission => `
                            <tr>
                                <td>
                                    <strong>${this.formatPermissionName(permission)}</strong>
                                    <br>
                                    <small class="text-muted">${permissions[permission].description}</small>
                                </td>
                                ${roleKeys.map(role => {
                                    const hasPermission = roles[role].permissions.includes(permission);
                                    return `
                                        <td class="${hasPermission ? 'permission-check' : 'permission-cross'}">
                                            <i class="bi ${hasPermission ? 'bi-check-lg' : 'bi-dash'}"></i>
                                        </td>
                                    `;
                                }).join('')}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;

        container.innerHTML = html;
    }

    displayAuditLogs() {
        const container = document.getElementById('auditLogsTable');
        if (!this.currentData.auditLogs || this.currentData.auditLogs.length === 0) {
            container.innerHTML = '<p class="text-muted text-center py-4">No audit logs found</p>';
            return;
        }

        const html = this.currentData.auditLogs.map(log => `
            <div class="audit-log-item ${log.success ? 'audit-log-success' : 'audit-log-failed'}">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <div class="audit-action">${this.formatActionName(log.action)}</div>
                        <div class="audit-details">${log.details}</div>
                        <div class="audit-timestamp">
                            <i class="bi bi-clock me-1"></i>
                            ${new Date(log.timestamp).toLocaleString()}
                        </div>
                    </div>
                    <div>
                        <span class="badge ${log.success ? 'bg-success' : 'bg-danger'}">
                            ${log.success ? 'Success' : 'Failed'}
                        </span>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    showAddUserModal() {
        // Reset form
        document.getElementById('addUserForm').reset();
        this.togglePasswordSection(true);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('addUserModal'));
        modal.show();
    }

    showCreateOrgModal() {
        // Reset form
        document.getElementById('createOrgForm').reset();
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('createOrgModal'));
        modal.show();
    }

    togglePasswordSection(show) {
        const passwordSection = document.getElementById('passwordSection');
        passwordSection.style.display = show ? 'block' : 'none';
        
        const passwordInput = document.getElementById('userPassword');
        passwordInput.required = show;
    }

    async saveUser() {
        try {
            this.showLoadingModal();

            const formData = {
                org_id: this.currentOrgId,
                email: document.getElementById('userEmail').value,
                first_name: document.getElementById('userFirstName').value,
                last_name: document.getElementById('userLastName').value,
                role: document.getElementById('userRole').value,
                is_sso_user: document.getElementById('isSSOUser').checked,
                password: document.getElementById('userPassword').value
            };

            const response = await fetch(`${this.apiBase}/users`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();
            this.hideLoadingModal();

            if (result.status === 'success') {
                this.showStatus('User created successfully', 'success');
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('addUserModal'));
                modal.hide();
                
                // Reload users
                await this.loadUserData();
            } else {
                throw new Error(result.message || 'Failed to create user');
            }

        } catch (error) {
            this.hideLoadingModal();
            console.error('Error creating user:', error);
            this.showStatus('Failed to create user', 'error');
        }
    }

    async saveOrganization() {
        try {
            this.showLoadingModal();

            const formData = {
                name: document.getElementById('orgName').value,
                domain: document.getElementById('orgDomain').value,
                industry: document.getElementById('orgIndustry').value,
                employee_count: parseInt(document.getElementById('orgEmployeeCount').value),
                billing_contact: document.getElementById('orgBillingContact').value,
                technical_contact: document.getElementById('orgTechnicalContact').value
            };

            const response = await fetch(`${this.apiBase}/organizations`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();
            this.hideLoadingModal();

            if (result.status === 'success') {
                this.showStatus('Organization created successfully', 'success');
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('createOrgModal'));
                modal.hide();
                
                // Update UI as needed
            } else {
                throw new Error(result.message || 'Failed to create organization');
            }

        } catch (error) {
            this.hideLoadingModal();
            console.error('Error creating organization:', error);
            this.showStatus('Failed to create organization', 'error');
        }
    }

    populateRoleSelectors() {
        const selectors = ['userRole', 'roleFilter'];
        const roles = this.currentData.roles;

        selectors.forEach(selectorId => {
            const selector = document.getElementById(selectorId);
            if (!selector) return;

            // Clear existing options (except first)
            while (selector.children.length > 1) {
                selector.removeChild(selector.lastChild);
            }

            // Add role options
            Object.keys(roles).forEach(roleKey => {
                const option = document.createElement('option');
                option.value = roleKey;
                option.textContent = this.formatRoleName(roleKey);
                selector.appendChild(option);
            });
        });
    }

    filterUsers() {
        const searchTerm = document.getElementById('userSearch').value.toLowerCase();
        const roleFilter = document.getElementById('roleFilter').value;

        let filteredUsers = this.currentData.users;

        // Apply search filter
        if (searchTerm) {
            filteredUsers = filteredUsers.filter(user => 
                user.first_name.toLowerCase().includes(searchTerm) ||
                user.last_name.toLowerCase().includes(searchTerm) ||
                user.email.toLowerCase().includes(searchTerm)
            );
        }

        // Apply role filter
        if (roleFilter) {
            filteredUsers = filteredUsers.filter(user => user.role === roleFilter);
        }

        // Store original users and temporarily replace for display
        const originalUsers = this.currentData.users;
        this.currentData.users = filteredUsers;
        this.displayUsers();
        this.currentData.users = originalUsers;
    }

    filterAuditLogs() {
        const actionFilter = document.getElementById('auditActionFilter').value;

        let filteredLogs = this.currentData.auditLogs;

        if (actionFilter) {
            filteredLogs = filteredLogs.filter(log => log.action === actionFilter);
        }

        // Store original logs and temporarily replace for display
        const originalLogs = this.currentData.auditLogs;
        this.currentData.auditLogs = filteredLogs;
        this.displayAuditLogs();
        this.currentData.auditLogs = originalLogs;
    }

    handleTabChange(targetTab) {
        switch (targetTab) {
            case '#users':
                if (this.currentData.users.length === 0) {
                    this.loadUserData();
                }
                break;
            case '#roles':
                if (Object.keys(this.currentData.roles).length === 0) {
                    this.loadRoles();
                }
                break;
            case '#sso':
                this.displaySSOConfiguration();
                break;
            case '#audit':
                if (this.currentData.auditLogs.length === 0) {
                    this.loadAuditLogs();
                }
                break;
        }
    }

    displaySSOConfiguration() {
        const container = document.getElementById('ssoConfiguration');
        
        const html = `
            <div class="row">
                <div class="col-md-6">
                    <h6 class="mb-3">Available SSO Providers</h6>
                    <div class="sso-provider-card" onclick="userMgmt.configureSAML()">
                        <div class="sso-provider-logo">
                            <i class="bi bi-shield-check display-6 text-primary"></i>
                        </div>
                        <h6>SAML 2.0</h6>
                        <p class="text-muted mb-0">Enterprise SAML authentication</p>
                    </div>
                    <div class="sso-provider-card" onclick="userMgmt.configureOAuth()">
                        <div class="sso-provider-logo">
                            <i class="bi bi-microsoft display-6 text-info"></i>
                        </div>
                        <h6>Microsoft Azure AD</h6>
                        <p class="text-muted mb-0">Azure Active Directory integration</p>
                    </div>
                    <div class="sso-provider-card" onclick="userMgmt.configureOkta()">
                        <div class="sso-provider-logo">
                            <i class="bi bi-key display-6 text-warning"></i>
                        </div>
                        <h6>Okta</h6>
                        <p class="text-muted mb-0">Okta identity management</p>
                    </div>
                </div>
                <div class="col-md-6">
                    <h6 class="mb-3">Current Configuration</h6>
                    <div class="card">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <span>SSO Status</span>
                                <span class="sso-status sso-disabled">Disabled</span>
                            </div>
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <span>Provider</span>
                                <span class="text-muted">Not configured</span>
                            </div>
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <span>Auto-provision users</span>
                                <span class="text-muted">No</span>
                            </div>
                            <button class="btn btn-primary w-100" onclick="userMgmt.enableSSO()">
                                <i class="bi bi-plus-circle me-2"></i>Configure SSO
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
    }

    // User action methods
    viewUser(userId) {
        const user = this.currentData.users.find(u => u.user_id === userId);
        if (!user) return;

        const content = `
            <div class="row">
                <div class="col-md-4 text-center">
                    <div class="user-avatar mx-auto mb-3" style="width: 80px; height: 80px; font-size: 2rem;">
                        ${user.first_name.charAt(0)}${user.last_name.charAt(0)}
                    </div>
                    <h5>${user.first_name} ${user.last_name}</h5>
                    <p class="text-muted">${user.email}</p>
                </div>
                <div class="col-md-8">
                    <table class="table table-borderless">
                        <tr>
                            <td><strong>Role:</strong></td>
                            <td><span class="role-badge role-${user.role.replace('_', '-')}">${this.formatRoleName(user.role)}</span></td>
                        </tr>
                        <tr>
                            <td><strong>Status:</strong></td>
                            <td>${user.is_active ? '<span class="text-success">Active</span>' : '<span class="text-danger">Inactive</span>'}</td>
                        </tr>
                        <tr>
                            <td><strong>SSO User:</strong></td>
                            <td>${user.is_sso_user ? '<span class="text-success">Yes</span>' : '<span class="text-muted">No</span>'}</td>
                        </tr>
                        <tr>
                            <td><strong>MFA Enabled:</strong></td>
                            <td>${user.mfa_enabled ? '<span class="text-success">Yes</span>' : '<span class="text-muted">No</span>'}</td>
                        </tr>
                        <tr>
                            <td><strong>Last Login:</strong></td>
                            <td>${user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}</td>
                        </tr>
                        <tr>
                            <td><strong>Created:</strong></td>
                            <td>${new Date(user.created_at).toLocaleString()}</td>
                        </tr>
                    </table>
                </div>
            </div>
        `;

        document.getElementById('userDetailsContent').innerHTML = content;
        const modal = new bootstrap.Modal(document.getElementById('userDetailsModal'));
        modal.show();
    }

    editUser(userId) {
        // Implementation for editing user
        console.log('Edit user:', userId);
        this.showStatus('Edit user functionality would be implemented here', 'info');
    }

    deleteUser(userId) {
        if (confirm('Are you sure you want to delete this user?')) {
            // Implementation for deleting user
            console.log('Delete user:', userId);
            this.showStatus('Delete user functionality would be implemented here', 'warning');
        }
    }

    // SSO Configuration methods
    configureSAML() {
        this.showStatus('SAML configuration would be implemented here', 'info');
    }

    configureOAuth() {
        this.showStatus('OAuth configuration would be implemented here', 'info');
    }

    configureOkta() {
        this.showStatus('Okta configuration would be implemented here', 'info');
    }

    enableSSO() {
        this.showStatus('SSO enablement would be implemented here', 'info');
    }

    exportAuditLogs() {
        // Create CSV content
        const headers = ['Timestamp', 'Action', 'User', 'Details', 'Success'];
        const csvContent = [
            headers.join(','),
            ...this.currentData.auditLogs.map(log => [
                new Date(log.timestamp).toISOString(),
                log.action,
                log.user_id || 'System',
                `"${log.details.replace(/"/g, '""')}"`,
                log.success ? 'Yes' : 'No'
            ].join(','))
        ].join('\n');

        // Download CSV file
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `audit-logs-${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);

        this.showStatus('Audit logs exported successfully', 'success');
    }

    logout() {
        if (confirm('Are you sure you want to logout?')) {
            // Implementation for logout
            window.location.href = 'index.html';
        }
    }

    // Utility methods
    formatRoleName(role) {
        return role.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    formatPermissionName(permission) {
        return permission.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    formatActionName(action) {
        return action.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    showStatus(message, type = 'info') {
        const alertElement = document.getElementById('statusAlert');
        const messageElement = document.getElementById('statusMessage');
        
        alertElement.className = `alert alert-${type} d-flex align-items-center`;
        messageElement.textContent = message;
        alertElement.style.display = 'block';

        if (type === 'success') {
            setTimeout(() => this.hideStatus(), 3000);
        }
    }

    hideStatus() {
        document.getElementById('statusAlert').style.display = 'none';
    }

    showLoadingModal() {
        const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
        modal.show();
    }

    hideLoadingModal() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
        if (modal) {
            modal.hide();
        }
    }
}

// Initialize the user management system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.userMgmt = new UserManagementSystem();
});