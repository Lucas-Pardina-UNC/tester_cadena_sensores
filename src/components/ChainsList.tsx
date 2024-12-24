/* import React from "react";
import { useChainsContext } from "./ChainsContext";

const ChainsList: React.FC = () => {
  const { chains } = useChainsContext();

  return (
    <div>
      <h3>Chains List</h3>
      <ul>
        {chains.map((chain) => (
          <li key={chain.id}>
            <strong>ID:</strong> {chain.id} | <strong>Port:</strong>{" "}
            {chain.chain_port}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ChainsList; */
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
