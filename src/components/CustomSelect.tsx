import React, { useState, useRef, useEffect } from "react";
import ReactDOM from "react-dom";

interface CustomSelectProps {
  direction: "down" | "right";
  options: React.ReactNode[];
  placeholder: string;
  selected?: string;
  onSelect?: (value: string) => void;
  closeAllDropdowns?: () => void; // Callback to close parent dropdowns
}

const CustomSelect: React.FC<CustomSelectProps> = ({
  direction,
  options,
  placeholder,
  selected: initialSelected = "",
  onSelect,
  closeAllDropdowns,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  //const [selectedOption, setSelectedOption] = useState<string>(initialSelected);
  const [selectedOption] = useState<string>(initialSelected);
  const dropdownRef = useRef<HTMLDivElement | null>(null);
  const [dropdownPosition, setDropdownPosition] = useState<{
    top: number;
    left: number;
  }>({ top: 0, left: 0 });

  const toggleDropdown = () => {
    setIsOpen((prev) => !prev);
  };

  const handleClickOutside = (event: MouseEvent) => {
    if (
      dropdownRef.current &&
      !dropdownRef.current.contains(event.target as Node)
    ) {
      setIsOpen(false);
    }
  };

  useEffect(() => {
    document.addEventListener("click", handleClickOutside);
    return () => {
      document.removeEventListener("click", handleClickOutside);
    };
  }, []);

  const handleOptionClick = (
    value: string,
    isCustomSelect: boolean,
    event: React.MouseEvent<HTMLDivElement>
  ) => {
    event.stopPropagation(); // Prevent the click from closing dropdowns unnecessarily
    if (!isCustomSelect) {
      //setSelectedOption(value);
      setIsOpen(false); // Close current dropdown
      closeAllDropdowns?.(); // Notify parent dropdown to close
      if (onSelect) onSelect(value); // Notify parent component of selection
    }
  };

  useEffect(() => {
    if (isOpen && dropdownRef.current) {
      const rect = dropdownRef.current.getBoundingClientRect();
      setDropdownPosition({
        top: direction === "down" ? rect.bottom : rect.top,
        left: direction === "down" ? rect.left : rect.right,
      });
    }
  }, [isOpen, direction]);

  return (
    <div className="custom-select" ref={dropdownRef}>
      <div className="selected" onClick={toggleDropdown}>
        {selectedOption || placeholder}
        <span className={`arrow ${direction}`}></span>
      </div>

      {isOpen &&
        ReactDOM.createPortal(
          <div
            className={`options ${direction}`}
            style={{
              position: "absolute",
              top: dropdownPosition.top,
              left: dropdownPosition.left,
            }}
          >
            {options.map((option, index) => {
              const isCustomSelect =
                React.isValidElement(option) && option.type === CustomSelect;

              return (
                <div
                  key={index}
                  className="option"
                  onClick={(e) =>
                    handleOptionClick(`option-${index}`, isCustomSelect, e)
                  }
                >
                  {isCustomSelect
                    ? React.cloneElement(option as React.ReactElement<any>, {
                        closeAllDropdowns: () => {
                          setIsOpen(false);
                          closeAllDropdowns?.();
                        },
                      })
                    : option}
                </div>
              );
            })}
          </div>,
          document.body
        )}
    </div>
  );
};

export default CustomSelect;
