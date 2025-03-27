import React from "react";
import { useChainsContext } from "./ChainsContext";
import Chain from "./Chain";

const ChainsList: React.FC = () => {
  const { chains } = useChainsContext();

  if (!chains || !chains.length) {
    return <div>No chains available</div>;
  }

  return (
    <div>
      <h3>Chains List</h3>
      <div>
        {chains.map((chain) => (
          <Chain key={chain.id} chain={chain} isExpanded={false} />
        ))}
      </div>
    </div>
  );
};

export default ChainsList;
