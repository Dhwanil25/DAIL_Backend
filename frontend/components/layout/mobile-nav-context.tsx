"use client";

import React, { createContext, useContext, useState } from 'react';

type MobileNavContextType = {
    isOpen: boolean;
    setIsOpen: (isOpen: boolean) => void;
};

const MobileNavContext = createContext<MobileNavContextType | undefined>(undefined);

export function MobileNavProvider({ children }: { children: React.ReactNode }) {
    const [isOpen, setIsOpen] = useState(false);
    return (
        <MobileNavContext.Provider value={{ isOpen, setIsOpen }}>
            {children}
        </MobileNavContext.Provider>
    );
}

export function useMobileNav() {
    const context = useContext(MobileNavContext);
    if (!context) {
        throw new Error('useMobileNav must be used within a MobileNavProvider');
    }
    return context;
}
