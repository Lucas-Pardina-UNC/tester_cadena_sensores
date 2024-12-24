// CustomAlertContext.tsx
import React, { createContext, useState, useContext, ReactNode } from "react";

interface AlertContextType {
  showAlert: (message: string) => Promise<void>;
}

const AlertContext = createContext<AlertContextType | undefined>(undefined);

export const useAlert = (): AlertContextType => {
  const context = useContext(AlertContext);
  if (!context) {
    throw new Error("useAlert must be used within an AlertProvider");
  }
  return context;
};

export const AlertProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [message, setMessage] = useState("");
  const [resolvePromise, setResolvePromise] = useState<(() => void) | null>(
    null
  );

  const showAlert = (message: string): Promise<void> => {
    return new Promise<void>((resolve) => {
      setMessage(message);
      setIsVisible(true);
      setResolvePromise(() => resolve);
    });
  };

  const handleClose = () => {
    setIsVisible(false);
    if (resolvePromise) {
      resolvePromise();
      setResolvePromise(null);
    }
  };

  return (
    <AlertContext.Provider value={{ showAlert }}>
      {children}
      {isVisible && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            backgroundColor: "rgba(0, 0, 0, 0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
          }}
        >
          <div
            style={{
              background: "white",
              padding: "20px",
              borderRadius: "8px",
              textAlign: "center",
              boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
            }}
          >
            <p>{message}</p>
            <button onClick={handleClose} style={{ marginTop: "10px" }}>
              OK
            </button>
          </div>
        </div>
      )}
    </AlertContext.Provider>
  );
};
