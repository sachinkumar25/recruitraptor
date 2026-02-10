
import { v4 as uuidv4 } from 'uuid';

export interface JobProfile {
    id: string;
    title: string;
    department: string;
    location: string;
    description: string; // The full JD text
    createdAt: string;
}

const STORAGE_KEY = 'recruitraptor_jobs';

// Mock initial data
const INITIAL_JOBS: JobProfile[] = [
    {
        id: '1',
        title: 'Senior Frontend Engineer',
        department: 'Engineering',
        location: 'Remote',
        description: `We are looking for a Senior Frontend Engineer to join our team. 
        Requirements:
        - 5+ years of experience with React, TypeScript, and Tailwind CSS.
        - Experience with Next.js and specialized UI libraries.
        - Strong understanding of web performance and accessibility.`,
        createdAt: new Date().toISOString(),
    },
    {
        id: '2',
        title: 'Product Manager',
        department: 'Product',
        location: 'San Francisco, CA',
        description: `Product Manager needed to lead our recruitment platform initiatives.
        - Define product roadmap and strategy.
        - Work closely with engineering and design teams.
        - Conduct user research and gather feedback.`,
        createdAt: new Date(Date.now() - 86400000).toISOString(),
    }
];

export const JobService = {
    getAll: (): JobProfile[] => {
        if (typeof window === 'undefined') return [];

        const stored = localStorage.getItem(STORAGE_KEY);
        if (!stored) {
            // Initialize with mock data if empty
            localStorage.setItem(STORAGE_KEY, JSON.stringify(INITIAL_JOBS));
            return INITIAL_JOBS;
        }

        try {
            return JSON.parse(stored);
        } catch (e) {
            console.error('Failed to parse jobs', e);
            return [];
        }
    },

    getById: (id: string): JobProfile | undefined => {
        const jobs = JobService.getAll();
        return jobs.find(job => job.id === id);
    },

    create: (job: Omit<JobProfile, 'id' | 'createdAt'>): JobProfile => {
        const jobs = JobService.getAll();
        const newJob: JobProfile = {
            ...job,
            id: uuidv4(),
            createdAt: new Date().toISOString(),
        };

        const updatedJobs = [newJob, ...jobs];
        localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedJobs));
        return newJob;
    },

    delete: (id: string): void => {
        const jobs = JobService.getAll();
        const updatedJobs = jobs.filter(job => job.id !== id);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedJobs));
    }
};
