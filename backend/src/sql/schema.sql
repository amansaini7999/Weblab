-- MVP schema for weblab business logic persistence.

create table if not exists weblabs (
    id text primary key,
    name text not null,
    assignment_mode text not null check (assignment_mode in ('session_based', 'user_based')),
    treatment_set text not null check (treatment_set in ('C,T1', 'C,T1,T2')),
    allocation_map jsonb,
    active_version integer,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists weblab_versions (
    weblab_id text not null references weblabs(id) on delete cascade,
    version integer not null,
    splits jsonb not null,
    created_at timestamptz not null default now(),
    primary key (weblab_id, version)
);

create table if not exists weblab_audit (
    id uuid primary key,
    weblab_id text not null references weblabs(id) on delete cascade,
    action text not null,
    detail text not null,
    created_at timestamptz not null default now()
);
