import { describe, it, expect } from 'vitest';
import { User } from '../types';

/**
 * Route protection and permission rule helper mirroring AuthContext / ProtectedRoute guards.
 */
function canAccessRoute(
  user: User | null,
  route: string
): { allowed: boolean; redirectTo?: string } {
  if (!user) {
    return { allowed: false, redirectTo: '/login' };
  }

  const adminOnlyRoutes = ['/hubs', '/analytics'];
  if (adminOnlyRoutes.includes(route) && user.role !== 'administrator') {
    return { allowed: false, redirectTo: '/' };
  }

  return { allowed: true };
}

function getEffectiveHubScope(user: User): string | null {
  if (user.role === 'administrator') {
    return null; // Global cross-hub visibility
  }
  return user.hub_id || null;
}

describe('Authentication & Role Guards', () => {
  const operatorUser: User = {
    id: 'user-op-1',
    username: 'operator_meru',
    email: 'operator@meru.bt.co.ke',
    role: 'operator',
    hub_id: 'hub-meru-1',
    preferred_language: 'sw',
  };

  const adminUser: User = {
    id: 'user-admin-1',
    username: 'admin',
    email: 'admin@bt.co.ke',
    role: 'administrator',
    preferred_language: 'en',
  };

  it('redirects unauthenticated users to /login', () => {
    expect(canAccessRoute(null, '/')).toEqual({ allowed: false, redirectTo: '/login' });
    expect(canAccessRoute(null, '/batches/123')).toEqual({ allowed: false, redirectTo: '/login' });
    expect(canAccessRoute(null, '/hubs')).toEqual({ allowed: false, redirectTo: '/login' });
    expect(canAccessRoute(null, '/analytics')).toEqual({ allowed: false, redirectTo: '/login' });
  });

  it('allows operators to access active batches and history, but blocks admin pages', () => {
    expect(canAccessRoute(operatorUser, '/').allowed).toBe(true);
    expect(canAccessRoute(operatorUser, '/history').allowed).toBe(true);
    expect(canAccessRoute(operatorUser, '/alerts').allowed).toBe(true);
    expect(canAccessRoute(operatorUser, '/batches/123').allowed).toBe(true);

    // Blocked routes
    expect(canAccessRoute(operatorUser, '/hubs')).toEqual({ allowed: false, redirectTo: '/' });
    expect(canAccessRoute(operatorUser, '/analytics')).toEqual({ allowed: false, redirectTo: '/' });
  });

  it('allows administrators to access all pages including hubs and analytics', () => {
    expect(canAccessRoute(adminUser, '/').allowed).toBe(true);
    expect(canAccessRoute(adminUser, '/history').allowed).toBe(true);
    expect(canAccessRoute(adminUser, '/alerts').allowed).toBe(true);
    expect(canAccessRoute(adminUser, '/batches/123').allowed).toBe(true);
    expect(canAccessRoute(adminUser, '/hubs').allowed).toBe(true);
    expect(canAccessRoute(adminUser, '/analytics').allowed).toBe(true);
  });

  it('correctly scopes operator to assigned hub while giving admin global scope', () => {
    expect(getEffectiveHubScope(operatorUser)).toBe('hub-meru-1');
    expect(getEffectiveHubScope(adminUser)).toBeNull();
  });
});
