// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/// @title RadStablecoin
/// @notice A simple stablecoin implementation with collateral-based minting
/// @dev Inherits from ERC20 and Ownable
contract RadStablecoin is ERC20, Ownable {
    /// @notice The collateralization ratio (150%)
    uint256 public constant COLLATERAL_RATIO = 150;

    /// @notice The precision for price calculations (2 decimal places)
    uint256 public constant PRICE_PRECISION = 100;

    /// @notice Mapping to track collateral balances for each user
    mapping(address => uint256) public collateralBalances;

    /// @notice Initializes the RadStablecoin contract
    constructor() ERC20("RadStablecoin", "RAD") {}

    /// @notice Allows users to deposit LineaETH as collateral
    /// @dev The deposited amount is added to the user's collateral balance
    function depositCollateral() external payable {
        collateralBalances[msg.sender] += msg.value;
    }

   

    /// @notice Burns stablecoin (RAD) and returns the equivalent collateral to the user
    /// @dev Calculates collateral to return based on current LineaETH price and burns RAD tokens
    /// @param stablecoinAmount The amount of stablecoin to burn
    function burnStablecoin(uint256 stablecoinAmount) external {
        require(balanceOf(msg.sender) >= stablecoinAmount, "Insufficient stablecoin balance");

        uint256 collateralToReturn = (stablecoinAmount * COLLATERAL_RATIO * PRICE_PRECISION) / (100 * getCurrentPrice());
        _burn(msg.sender, stablecoinAmount);
        collateralBalances[msg.sender] += collateralToReturn;
    }

    /// @notice Gets the current price of LineaETH in USD
    /// @dev In a real-world scenario, this would fetch the price from an oracle
    /// @return The current LineaETH price in USD (fixed at $2000 for simplicity)
    function getCurrentPrice() public view returns (uint256) {
        // In a real-world scenario, this would fetch the current LineaETH/USD price from an oracle
        // For simplicity, we'll use a fixed price of $2000 per LineaETH
        return 200000; // $2000.00
    }
}