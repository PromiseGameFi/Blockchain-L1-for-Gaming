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

    /// @notice Allows users to withdraw their deposited collateral
    /// @dev Implements the checks-effects-interactions pattern to prevent reentrancy
    /// @param amount The amount of collateral to withdraw (in wei)
    function withdrawCollateral(uint256 amount) external {
        require(collateralBalances[msg.sender] >= amount, "Insufficient collateral");
        collateralBalances[msg.sender] -= amount; // Update state before making external call
        payable(msg.sender).transfer(amount);     // Safely transfer LineaETH after updating state
    }

    /// @notice Mints stablecoin (RAD) based on the user's deposited collateral
    /// @dev Calculates required collateral based on current LineaETH price and mints RAD tokens
    /// @param stablecoinAmount The amount of stablecoin to mint
    function mintStablecoin(uint256 stablecoinAmount) external {
        uint256 collateralRequired = (stablecoinAmount * COLLATERAL_RATIO * PRICE_PRECISION) / (100 * getCurrentPrice());
        require(collateralBalances[msg.sender] >= collateralRequired, "Insufficient collateral");

        collateralBalances[msg.sender] -= collateralRequired;
        _mint(msg.sender, stablecoinAmount);
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

    
}